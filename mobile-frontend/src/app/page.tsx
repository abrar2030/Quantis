import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Loader2,
  LogOut,
  BrainCircuit,
  History,
  Trash2,
  LineChart as LineChartIcon,
  UploadCloud,
  Database,
  Model,
} from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useAuth } from '@/context/AuthContext';
import { predictionsAPI, handleApiError } from '@/lib/api';

interface PredictionResponse {
  prediction: number[] | number;
  confidence: number;
}

interface HistoryEntry extends PredictionResponse {
  features: string;
  timestamp: number;
}

const formatChartData = (prediction: number[]) => {
  return prediction.map((value, index) => ({ name: `t+${index + 1}`, value }));
};

export default function Home() {
  const router = useRouter();
  const { user, logout, isLoading: authLoading } = useAuth();
  const [featureInput, setFeatureInput] = useState<string>('');
  const [predictionResult, setPredictionResult] =
    useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [predictionHistory, setPredictionHistory] = useState<HistoryEntry[]>(
    []
  );

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    const storedHistory = localStorage.getItem(`predictionHistory_${user?.id}`);
    if (storedHistory) {
      try {
        setPredictionHistory(JSON.parse(storedHistory));
      } catch (e) {
        console.error('Failed to parse prediction history:', e);
        localStorage.removeItem(`predictionHistory_${user?.id}`);
      }
    }
  }, [user]);

  useEffect(() => {
    if (user && predictionHistory.length > 0) {
      localStorage.setItem(
        `predictionHistory_${user.id}`,
        JSON.stringify(predictionHistory)
      );
    } else if (user) {
      localStorage.removeItem(`predictionHistory_${user.id}`);
    }
  }, [predictionHistory, user]);

  const handlePredict = async () => {
    if (!user) {
      setError('User not authenticated. Please log in.');
      router.push('/login');
      return;
    }

    setIsLoading(true);
    setError(null);
    setPredictionResult(null);

    try {
      const features = featureInput
        .split(',')
        .map((f) => parseFloat(f.trim()))
        .filter((f) => !isNaN(f));
      if (features.length === 0 || features.some(isNaN)) {
        throw new Error(
          'Invalid feature input. Please enter comma-separated numbers.'
        );
      }

      const response = await predictionsAPI.createPrediction({ features });
      setPredictionResult(response);

      const newHistoryEntry: HistoryEntry = {
        ...response,
        features: featureInput,
        timestamp: Date.now(),
      };
      setPredictionHistory((prevHistory) =>
        [newHistoryEntry, ...prevHistory].slice(0, 10)
      );
    } catch (err: any) {
      const apiError = handleApiError(err);
      setError(apiError.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const clearHistory = () => {
    setPredictionHistory([]);
  };

  if (authLoading || !user) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <Loader2 className="h-12 w-12 animate-spin text-blue-400 mb-4" />
        <p className="text-lg text-gray-300">Loading session...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <Card className="w-full max-w-lg bg-gray-800/80 backdrop-blur-sm border border-gray-700 shadow-xl rounded-xl overflow-hidden">
        <CardHeader className="text-center p-6 bg-gray-800/50 border-b border-gray-700">
          <div className="flex justify-center items-center mb-3">
            <BrainCircuit className="h-8 w-8 text-blue-400 mr-2" />
            <CardTitle className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Quantis Predictor
            </CardTitle>
          </div>
          <CardDescription className="text-gray-400">
            Welcome back,{' '}
            <span className="font-medium text-gray-300">
              {user.username || user.email || 'User'}
            </span>
            ! Input features for prediction.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <div className="space-y-2">
            <Label
              htmlFor="features"
              className="text-sm font-medium text-gray-300"
            >
              Input Features
            </Label>
            <Input
              id="features"
              placeholder="e.g., 1.2, 3.4, 5.6, ..."
              value={featureInput}
              onChange={(e) => setFeatureInput(e.target.value)}
              className="bg-gray-700 border-gray-600 text-white placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3"
            />
            <p className="text-xs text-gray-500">
              Enter numerical features separated by commas.
            </p>
          </div>
          <Button
            onClick={handlePredict}
            disabled={isLoading || !featureInput || !user}
            className="w-full text-lg font-semibold py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Predicting...
              </>
            ) : (
              'Get Prediction'
            )}
          </Button>

          {error && (
            <Alert
              variant="destructive"
              className="w-full bg-red-900/30 border-red-700 text-red-300 rounded-lg"
            >
              <AlertTitle className="font-semibold">Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {predictionResult && (
            <Alert
              variant="default"
              className="w-full bg-gray-700/50 border-gray-600 text-gray-300 rounded-lg"
            >
              <AlertTitle className="font-semibold flex items-center mb-2">
                <LineChartIcon className="h-5 w-5 mr-2 text-blue-400" />{' '}
                Prediction Result
              </AlertTitle>
              <AlertDescription className="space-y-2">
                {Array.isArray(predictionResult.prediction) ? (
                  <div className="h-[200px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={formatChartData(predictionResult.prediction)}
                        margin={{ top: 5, right: 20, left: -10, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#4B5563" />
                        <XAxis dataKey="name" stroke="#9CA3AF" fontSize={12} />
                        <YAxis stroke="#9CA3AF" fontSize={12} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1F2937',
                            border: '1px solid #4B5563',
                            borderRadius: '0.5rem',
                          }}
                          labelStyle={{ color: '#E5E7EB' }}
                          itemStyle={{ color: '#60A5FA' }}
                        />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Line
                          type="monotone"
                          dataKey="value"
                          name="Prediction"
                          stroke="#60A5FA"
                          strokeWidth={2}
                          activeDot={{ r: 6 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="text-lg">
                    Prediction:{' '}
                    <span className="font-bold text-blue-300">
                      {JSON.stringify(predictionResult.prediction)}
                    </span>
                  </p>
                )}
                <p className="text-sm pt-1">
                  Confidence:{' '}
                  <span className="font-semibold text-green-400">
                    {(predictionResult.confidence * 100).toFixed(2)}%
                  </span>
                </p>
              </AlertDescription>
            </Alert>
          )}

          {predictionHistory.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-700">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-xl font-semibold text-gray-300 flex items-center">
                  <History className="mr-2 h-5 w-5 text-purple-400" />{' '}
                  Prediction History
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearHistory}
                  className="text-red-400 hover:text-red-300 hover:bg-red-900/30"
                >
                  <Trash2 className="mr-1 h-4 w-4" /> Clear
                </Button>
              </div>
              <ScrollArea className="h-[200px] w-full rounded-md border border-gray-700 bg-gray-900/50 p-3">
                <div className="space-y-3">
                  {predictionHistory.map((entry) => (
                    <div
                      key={entry.timestamp}
                      className="text-sm p-2 rounded bg-gray-700/50"
                    >
                      <p className="text-xs text-gray-500 mb-1">
                        {new Date(entry.timestamp).toLocaleString()}
                      </p>
                      <p className="text-gray-400 truncate">
                        <span className="font-medium text-gray-300">
                          Input:
                        </span>{' '}
                        {entry.features}
                      </p>
                      <p className="text-blue-300">
                        <span className="font-medium text-gray-300">Pred:</span>{' '}
                        {JSON.stringify(entry.prediction)} (
                        <span className="font-medium text-gray-300">Conf:</span>{' '}
                        {(entry.confidence * 100).toFixed(1)}%)
                      </p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex flex-col items-center p-6 bg-gray-800/50 border-t border-gray-700">
          <div className="flex space-x-4 mb-4">
            <Button
              variant="outline"
              onClick={() => router.push('/datasets')}
              className="bg-transparent border-gray-600 hover:bg-gray-700/50 text-gray-300 hover:text-white rounded-lg flex items-center justify-center"
            >
              <Database className="mr-2 h-4 w-4" /> Datasets
            </Button>
            <Button
              variant="outline"
              onClick={() => router.push('/models')}
              className="bg-transparent border-gray-600 hover:bg-gray-700/50 text-gray-300 hover:text-white rounded-lg flex items-center justify-center"
            >
              <Model className="mr-2 h-4 w-4" /> Models
            </Button>
          </div>
          <Button
            variant="outline"
            onClick={handleLogout}
            className="w-full bg-transparent border-gray-600 hover:bg-gray-700/50 text-gray-300 hover:text-white rounded-lg flex items-center justify-center"
          >
            <LogOut className="mr-2 h-4 w-4" /> Logout
          </Button>
        </CardFooter>
      </Card>
    </main>
  );
}
