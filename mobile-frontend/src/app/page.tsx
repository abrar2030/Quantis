
'use client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

// Define the structure for the prediction response based on schemas.py
interface PredictionResponse {
  prediction: number[] | number; // Adjust based on actual model output shape
  confidence: number;
}

export default function Home() {
  const router = useRouter();
  // State for input features
  const [featureInput, setFeatureInput] = useState<string>('');
  const [apiKey, setApiKey] = useState<string | null>(null); // State for API Key, initially null
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Effect to check for API key on component mount
  useEffect(() => {
    const storedApiKey = localStorage.getItem('apiKey');
    const storedEmail = localStorage.getItem('userEmail');
    if (storedApiKey) {
      setApiKey(storedApiKey);
      setUserEmail(storedEmail);
    } else {
      // If no API key, redirect to login
      router.push('/login');
    }
  }, [router]);

  const handlePredict = async () => {
    if (!apiKey) {
      setError('API Key not found. Please log in again.');
      router.push('/login');
      return;
    }

    setIsLoading(true);
    setError(null);
    setPredictionResult(null);

    try {
      // Use the Next.js API route proxy
      const apiUrl = process.env.NEXT_PUBLIC_API_PROXY_URL ? `${process.env.NEXT_PUBLIC_API_PROXY_URL}/predict` : '/api/predict';

      // Validate and parse features (comma-separated numbers)
      const features = featureInput.split(',').map(f => parseFloat(f.trim())).filter(f => !isNaN(f));
      if (features.length === 0 || features.some(isNaN)) {
        throw new Error('Invalid feature input. Please enter comma-separated numbers.');
      }

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Pass API key in header
          'X-API-Key': apiKey
        },
        body: JSON.stringify({ features: features })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API request failed with status ${response.status}`);
      }

      const data: PredictionResponse = await response.json();
      setPredictionResult(data);

    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('apiKey');
    localStorage.removeItem('userEmail');
    setApiKey(null);
    setUserEmail(null);
    router.push('/login');
  };

  // Render loading or login redirect state
  if (apiKey === null) {
    return (
        <main className="flex min-h-screen items-center justify-center p-4 sm:p-8 bg-gray-100 dark:bg-gray-900">
            <p>Loading or redirecting...</p>
        </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4 sm:p-8 bg-gray-100 dark:bg-gray-900">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">Quantis Model Prediction</CardTitle>
          <CardDescription className="text-center text-gray-600 dark:text-gray-400">
            Welcome, {userEmail || 'User'}! Enter features to get a prediction.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* API Key input removed, now fetched from localStorage */}
          <div className="space-y-2">
            <Label htmlFor="features">Features (comma-separated)</Label>
            <Input
              id="features"
              placeholder="e.g., 1.2, 3.4, 5.6"
              value={featureInput}
              onChange={(e) => setFeatureInput(e.target.value)}
              className="dark:bg-gray-800 dark:text-white"
            />
          </div>
          <Button onClick={handlePredict} disabled={isLoading || !featureInput || !apiKey} className="w-full">
            {isLoading ? 'Predicting...' : 'Get Prediction'}
          </Button>
        </CardContent>
        <CardFooter className="flex flex-col items-center space-y-4">
          {error && (
            <p className="text-red-500 text-sm text-center">Error: {error}</p>
          )}
          {predictionResult && (
            <div className="text-center p-4 border rounded-md bg-gray-50 dark:bg-gray-800 w-full">
              <p className="text-lg font-semibold">Prediction: <span className="text-blue-600 dark:text-blue-400">{JSON.stringify(predictionResult.prediction)}</span></p>
              <p className="text-md">Confidence: <span className="text-green-600 dark:text-green-400">{(predictionResult.confidence * 100).toFixed(2)}%</span></p>
            </div>
          )}
           <Button variant="outline" onClick={handleLogout} className="w-full mt-4">
            Logout
          </Button>
        </CardFooter>
      </Card>
    </main>
  );
}
