// Express App Entry Point
const express = require('express');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('SiteFlow API Gateway is running!');
});

// Forward /forecast requests to Go orchestrator
app.get('/forecast', async (req, res) => {
  try {
    // Forward all query params
    const goUrl = `http://localhost:8080/forecast${req.url.replace('/forecast', '')}`;
    const response = await axios.get(goUrl);
    res.status(response.status).json(response.data);
  } catch (err) {
    res.status(502).json({ error: 'Failed to reach Go orchestrator', details: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`API Gateway listening on port ${PORT}`);
});
