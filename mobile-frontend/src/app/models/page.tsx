import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { modelsAPI, handleApiError } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Loader2,
  PlusCircle,
  BrainCircuit,
  Trash2,
  Eye,
  Play,
} from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

interface Model {
  id: string;
  name: string;
  description: string;
  model_type: string;
  status: string;
  created_at: string;
  trained_at?: string;
  metrics?: {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1_score?: number;
    mse?: number;
    rmse?: number;
    mae?: number;
    r2?: number;
  };
}

export default function Models() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [models, setModels] = useState<Model[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      fetchModels();
    }
  }, [user, authLoading, router]);

  const fetchModels = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await modelsAPI.getModels();
      setModels(response.data);
    } catch (err: any) {
      const apiError = handleApiError(err);
      setError(apiError.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteModel = async (modelId: string) => {
    if (window.confirm('Are you sure you want to delete this model?')) {
      try {
        await modelsAPI.deleteModel(modelId);
        fetchModels(); // Refresh the list
      } catch (err: any) {
        const apiError = handleApiError(err);
        setError(apiError.message);
      }
    }
  };

  const handleTrainModel = async (modelId: string) => {
    if (
      window.confirm(
        'Are you sure you want to train this model? This may take some time.'
      )
    ) {
      try {
        await modelsAPI.trainModel(modelId);
        fetchModels(); // Refresh the list to show updated status
      } catch (err: any) {
        const apiError = handleApiError(err);
        setError(apiError.message);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'trained':
        return 'text-green-400';
      case 'training':
        return 'text-yellow-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  if (authLoading || isLoading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <Loader2 className="h-12 w-12 animate-spin text-blue-400 mb-4" />
        <p className="text-lg text-gray-300">Loading models...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <Card className="w-full max-w-3xl bg-gray-800/80 backdrop-blur-sm border border-gray-700 shadow-xl rounded-xl overflow-hidden mb-8">
        <CardHeader className="text-center p-6 bg-gray-800/50 border-b border-gray-700">
          <CardTitle className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Your Models
          </CardTitle>
          <CardDescription className="text-gray-400">
            Manage your machine learning models and view their performance.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          {error && (
            <Alert
              variant="destructive"
              className="w-full bg-red-900/30 border-red-700 text-red-300 rounded-lg"
            >
              <AlertTitle className="font-semibold">Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button
            onClick={() => router.push('/models/create')}
            className="w-full text-lg font-semibold py-3 rounded-lg bg-gradient-to-r from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700 transition-all duration-300 ease-in-out flex items-center justify-center"
          >
            <PlusCircle className="mr-2 h-5 w-5" /> Create New Model
          </Button>

          <Separator className="bg-gray-700" />

          {models.length === 0 ? (
            <div className="text-center py-8">
              <BrainCircuit className="mx-auto h-16 w-16 text-gray-500 mb-4" />
              <p className="text-gray-400 text-lg">No models created yet.</p>
              <p className="text-gray-500">
                Start by creating your first model!
              </p>
            </div>
          ) : (
            <ScrollArea className="h-[400px] w-full rounded-md border border-gray-700 bg-gray-900/50 p-3">
              <div className="space-y-4">
                {models.map((model) => (
                  <Card
                    key={model.id}
                    className="bg-gray-700/50 border-gray-600"
                  >
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="text-xl font-semibold text-blue-300">
                            {model.name}
                          </h3>
                          <p className="text-sm text-gray-400">
                            {model.description || 'No description provided.'}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          {model.status === 'created' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleTrainModel(model.id)}
                              className="text-green-400 border-green-400 hover:bg-green-900/30"
                            >
                              <Play className="h-4 w-4" />
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => router.push(`/models/${model.id}`)}
                            className="text-blue-400 border-blue-400 hover:bg-blue-900/30"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteModel(model.id)}
                            className="text-red-400 border-red-400 hover:bg-red-900/30"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm text-gray-400">
                        <p>
                          <strong>Type:</strong> {model.model_type}
                        </p>
                        <p>
                          <strong>Status:</strong>{' '}
                          <span className={getStatusColor(model.status)}>
                            {model.status}
                          </span>
                        </p>
                        <p>
                          <strong>Created:</strong>{' '}
                          {new Date(model.created_at).toLocaleDateString()}
                        </p>
                        {model.trained_at && (
                          <p>
                            <strong>Trained:</strong>{' '}
                            {new Date(model.trained_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      {model.metrics && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500">
                            Accuracy:{' '}
                            {(model.metrics.accuracy * 100).toFixed(2)}%
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
