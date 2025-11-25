// This file will proxy requests to the backend API OR return a mock response for testing.
// It helps avoid CORS issues during development and abstracts the backend URL

import { NextApiRequest, NextApiResponse } from 'next';

// --- MOCKING FOR TESTING ---
const USE_MOCK_DATA = true;
// --- END MOCKING ---

// Define the backend API URL
const BACKEND_API_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

// Mock prediction function
const getMockPrediction = (features: number[]) => {
  const isSequence = features.length > 2;
  const prediction = isSequence
    ? features.map((f, i) =>
        parseFloat((f * 1.1 + i * 0.5 + Math.random() * 2).toFixed(2))
      )
    : parseFloat(
        (features.reduce((a, b) => a + b, 0) * 1.2 + Math.random()).toFixed(2)
      );

  const confidence = parseFloat((0.8 + Math.random() * 0.19).toFixed(4));

  return {
    prediction,
    confidence,
  };
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  // Extract features and API key
  const { features } = req.body;
  const apiKey = req.headers['x-api-key'] as string;

  // --- FIXED VALIDATION ---
  if (
    !features ||
    !Array.isArray(features) ||
    features.length === 0 ||
    features.some((v) => Number.isNaN(Number(v)))
  ) {
    return res
      .status(400)
      .json({ detail: 'Missing or invalid features array in request body' });
  }

  if (!apiKey) {
    console.warn('Missing X-API-Key header, but proceeding with mock data.');
  }

  // --- MOCK RESPONSE ---
  if (USE_MOCK_DATA) {
    console.log('Using mock data for prediction request.');
    await new Promise((resolve) => setTimeout(resolve, 500));
    const mockResponse = getMockPrediction(features as number[]);
    return res.status(200).json(mockResponse);
  }
  // --- END MOCK RESPONSE ---

  // --- REAL BACKEND PROXY ---
  try {
    const backendUrl = `${BACKEND_API_URL}/predict`;
    console.log(`Proxying request to: ${backendUrl}`);

    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
      body: JSON.stringify({ features }),
    });

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      console.error(`Backend API error (${backendResponse.status}):`, data);
      return res.status(backendResponse.status).json(data);
    }

    return res.status(200).json(data);
  } catch (error: any) {
    console.error('API proxy fetch error:', error);
    return res
      .status(502)
      .json({ detail: 'Bad Gateway: Error connecting to backend API' });
  }
  // --- END REAL BACKEND PROXY ---
}

// --- OPTIONAL FIX IF req.body shows undefined ---
// export const config = {
//   api: {
//     bodyParser: true,
//   },
// };
