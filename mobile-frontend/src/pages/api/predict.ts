// This file will proxy requests to the backend API
// It helps avoid CORS issues during development and abstracts the backend URL

import { NextApiRequest, NextApiResponse } from 'next';

// Define the backend API URL. Read from environment variable or use a default.
// The default assumes the backend runs locally on port 8000.
// This should be configured via environment variables in production.
const BACKEND_API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only allow POST requests for prediction
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  // Extract features from request body and API key from header
  const { features } = req.body;
  const apiKey = req.headers['x-api-key'] as string; // Ensure header key matches frontend and backend expectations

  // Basic validation
  if (!features || !Array.isArray(features) || features.length === 0) {
    return res.status(400).json({ detail: 'Missing or invalid features array in request body' });
  }
  if (!apiKey) {
    return res.status(400).json({ detail: 'Missing X-API-Key header' });
  }

  try {
    // Construct the full backend prediction endpoint URL
    const backendUrl = `${BACKEND_API_URL}/predict`;
    console.log(`Proxying request to: ${backendUrl}`); // Log backend URL for debugging

    // Make the request to the actual backend API
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Forward the API key. Ensure the backend's `validate_api_key` checks this header.
        'X-API-Key': apiKey,
      },
      // Ensure the features are sent in the format expected by the backend's PredictionRequest schema
      body: JSON.stringify({ features: features }),
    });

    // Read the response body from the backend
    const data = await backendResponse.json();

    // Check if the backend request was successful
    if (!backendResponse.ok) {
      // Forward the error status and message from the backend
      console.error(`Backend API error (${backendResponse.status}):`, data);
      return res.status(backendResponse.status).json(data);
    }

    // Forward the successful response from the backend to the frontend client
    return res.status(200).json(data);

  } catch (error: any) {
    // Handle network errors or issues connecting to the backend
    console.error('API proxy fetch error:', error);
    return res.status(502).json({ detail: 'Bad Gateway: Error connecting to backend API' });
  }
}
