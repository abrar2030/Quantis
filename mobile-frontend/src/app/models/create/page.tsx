import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { datasetsAPI, modelsAPI, handleApiError } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, PlusCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface Dataset {
  id: string;
  name: string;
  row_count: number;
}

export default function ModelCreate() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [newModel, setNewModel] = useState({
    name: '',
    description: '',
    model_type: 'linear_regression',
    dataset_id: '',
    target_column: '',
    feature_columns: [] as string[],
    hyperparameters: {},
  });

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      fetchDatasets();
    }
  }, [user, authLoading, router]);

  const fetchDatasets = async () => {
    try {
      const response = await datasetsAPI.getDatasets();
      setDatasets(response.data);
    } catch (err: any) {
      const apiError = handleApiError(err);
      setError(apiError.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateModel = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await modelsAPI.createModel(newModel);
      setSuccess('Model created successfully!');
      setNewModel({
        name: '',
        description: '',
        model_type: 'linear_regression',
        dataset_id: '',
        target_column: '',
        feature_columns: [],
        hyperparameters: {},
      });
      router.push('/models');
    } catch (err: any) {
      const apiError = handleApiError(err);
      setError(apiError.message);
    } finally {
      setIsLoading(false);
    }
  };

  const modelTypes = [
    { value: 'linear_regression', label: 'Linear Regression' },
    { value: 'random_forest', label: 'Random Forest' },
    { value: 'lstm', label: 'LSTM Neural Network' },
    { value: 'arima', label: 'ARIMA' },
    { value: 'tft', label: 'Temporal Fusion Transformer' },
  ];

  if (authLoading || isLoading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <Loader2 className="h-12 w-12 animate-spin text-blue-400 mb-4" />
        <p className="text-lg text-gray-300">Loading...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <Card className="w-full max-w-3xl bg-gray-800/80 backdrop-blur-sm border border-gray-700 shadow-xl rounded-xl overflow-hidden mb-8">
        <CardHeader className="text-center p-6 bg-gray-800/50 border-b border-gray-700">
          <CardTitle className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Create New Model
          </CardTitle>
          <CardDescription className="text-gray-400">
            Define your machine learning model and prepare it for training.
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
          {success && (
            <Alert
              variant="default"
              className="w-full bg-green-900/30 border-green-700 text-green-300 rounded-lg"
            >
              <AlertTitle className="font-semibold">Success</AlertTitle>
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            <div>
              <Label
                htmlFor="model-name"
                className="text-sm font-medium text-gray-300"
              >
                Model Name
              </Label>
              <Input
                id="model-name"
                placeholder="My Predictive Model"
                value={newModel.name}
                onChange={(e) =>
                  setNewModel((prev) => ({ ...prev, name: e.target.value }))
                }
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3"
                required
              />
            </div>
            <div>
              <Label
                htmlFor="description"
                className="text-sm font-medium text-gray-300"
              >
                Description (Optional)
              </Label>
              <Input
                id="description"
                placeholder="A brief description of my model"
                value={newModel.description}
                onChange={(e) =>
                  setNewModel((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3"
              />
            </div>
            <div>
              <Label
                htmlFor="model-type"
                className="text-sm font-medium text-gray-300"
              >
                Model Type
              </Label>
              <Select
                value={newModel.model_type}
                onValueChange={(value) =>
                  setNewModel((prev) => ({ ...prev, model_type: value }))
                }
              >
                <SelectTrigger className="w-full bg-gray-700 border-gray-600 text-white focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3">
                  <SelectValue placeholder="Select a model type" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700 text-white">
                  {modelTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label
                htmlFor="dataset"
                className="text-sm font-medium text-gray-300"
              >
                Dataset
              </Label>
              <Select
                value={newModel.dataset_id}
                onValueChange={(value) =>
                  setNewModel((prev) => ({ ...prev, dataset_id: value }))
                }
              >
                <SelectTrigger className="w-full bg-gray-700 border-gray-600 text-white focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3">
                  <SelectValue placeholder="Select a dataset" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700 text-white">
                  {datasets.map((dataset) => (
                    <SelectItem key={dataset.id} value={dataset.id}>
                      {dataset.name} ({dataset.row_count} rows)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {/* Add more fields for target_column, feature_columns, hyperparameters if needed */}
          </div>
        </CardContent>
        <CardFooter className="flex justify-center p-6 bg-gray-800/50 border-t border-gray-700">
          <Button
            onClick={handleCreateModel}
            disabled={!newModel.name || !newModel.dataset_id || isLoading}
            className="w-full sm:w-auto text-lg font-semibold py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Creating...
              </>
            ) : (
              <>
                <PlusCircle className="mr-2 h-5 w-5" /> Create Model
              </>
            )}
          </Button>
        </CardFooter>
      </Card>
    </main>
  );
}
