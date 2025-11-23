package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os/exec"
	"sync"
)

// Defines the contract with your Python script
type ForecastPoint struct {
	Date  string  `json:"date"`
	Value float64 `json:"value"`
}

type ModelResult struct {
	Model    string          `json:"model"`
	Forecast []ForecastPoint `json:"forecast"`
	Error    string          `json:"error,omitempty"`
}

// RunEnsemble launches a Python script for each model concurrently
func RunEnsemble(siteID int, models []string) []ModelResult {
	var wg sync.WaitGroup
	resultsChan := make(chan ModelResult, len(models))

	fmt.Println("⚡ Spawning Python workers...")

	// Fan-out: Start a Goroutine for each model
	for _, model := range models {
		wg.Add(1)
		go func(m string) {
			defer wg.Done()
			runPythonWorker(siteID, m, resultsChan)
		}(model)
	}

	// Wait for all to finish
	wg.Wait()
	close(resultsChan)

	// Collect results
	var results []ModelResult
	for res := range resultsChan {
		results = append(results, res)
	}
	return results
}

func runPythonWorker(siteID int, modelName string, results chan<- ModelResult) {
	// On Windows, use 'python' and call the correct model script
	var scriptPath string
	switch modelName {
	case "prophet":
		scriptPath = "models/forecast_prophet.py"
	case "sarima":
		scriptPath = "models/forecast_sarima.py"
	case "xgboost":
		scriptPath = "models/forecast_xgboost.py"
	default:
		results <- ModelResult{Model: modelName, Error: "Unknown model"}
		return
	}
	// Always use venv Python for consistent environment
	pythonExe := "venv/Scripts/python"
	cmd := exec.Command(pythonExe, scriptPath,
		"--site_id", fmt.Sprint(siteID),
	)

	// Capture stdout and stderr separately so we can return diagnostics
	stdoutPipe, err := cmd.StdoutPipe()
	if err != nil {
		results <- ModelResult{Model: modelName, Error: err.Error()}
		return
	}
	stderrPipe, err := cmd.StderrPipe()
	if err != nil {
		results <- ModelResult{Model: modelName, Error: err.Error()}
		return
	}

	if err := cmd.Start(); err != nil {
		results <- ModelResult{Model: modelName, Error: err.Error()}
		return
	}

	stdoutBytes, _ := io.ReadAll(stdoutPipe)
	stderrBytes, _ := io.ReadAll(stderrPipe)

	cmdErr := cmd.Wait()

	var result ModelResult
	if cmdErr != nil {
		// Include stderr content in the error for debugging
		fmt.Printf("❌ %s failed: %v\nstderr:\n%s\n", modelName, cmdErr, string(stderrBytes))
		result = ModelResult{Model: modelName, Error: fmt.Sprintf("%v: %s", cmdErr, string(stderrBytes))}
	} else {
		if len(stderrBytes) > 0 {
			// Informational: Python wrote to stderr but exited 0
			fmt.Printf("ℹ️ %s stderr:\n%s\n", modelName, string(stderrBytes))
		}
		// Parse JSON from Python stdout
		if jsonErr := json.Unmarshal(stdoutBytes, &result); jsonErr != nil {
			fmt.Printf("⚠️ %s returned invalid JSON: %v\nstdout:\n%s\n", modelName, jsonErr, string(stdoutBytes))
			result = ModelResult{Model: modelName, Error: "Invalid JSON"}
		} else {
			fmt.Printf("✅ %s finished successfully\n", modelName)
		}
	}
	results <- result
}
