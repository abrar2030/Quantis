import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { datasetsAPI, handleApiError } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, PlusCircle, FileText, Trash2, Eye } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

interface Dataset {
  id: string;
  name: string;
  description: string;
  row_count: number;
  columns: string[];
  file_size: number;
  created_at: string;
  metadata?: {
    numeric_columns?: string[];
    categorical_columns?: string[];
  };
}

export default function Datasets() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      fetchDatasets();
    }
  }, [user, authLoading, router]);

  const fetchDatasets = async () => {
    setIsLoading(true);
    setError(null);
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

  const handleDeleteDataset = async (datasetId: string) => {
    if (window.confirm('Are you sure you want to delete this dataset?')) {
      try {
        await datasetsAPI.deleteDataset(datasetId);
        fetchDatasets(); // Refresh the list
      } catch (err: any) {
        const apiError = handleApiError(err);
        setError(apiError.message);
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (authLoading || isLoading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <Loader2 className="h-12 w-12 animate-spin text-blue-400 mb-4" />
        <p className="text-lg text-gray-300">Loading datasets...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <Card className="w-full max-w-3xl bg-gray-800/80 backdrop-blur-sm border border-gray-700 shadow-xl rounded-xl overflow-hidden mb-8">
        <CardHeader className="text-center p-6 bg-gray-800/50 border-b border-gray-700">
          <CardTitle className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Your Datasets
          </CardTitle>
          <CardDescription className="text-gray-400">
            Manage your uploaded datasets and prepare them for model training.
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
            onClick={() => router.push('/datasets/upload')}
            className="w-full text-lg font-semibold py-3 rounded-lg bg-gradient-to-r from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700 transition-all duration-300 ease-in-out flex items-center justify-center"
          >
            <PlusCircle className="mr-2 h-5 w-5" /> Upload New Dataset
          </Button>

          <Separator className="bg-gray-700" />

          {datasets.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="mx-auto h-16 w-16 text-gray-500 mb-4" />
              <p className="text-gray-400 text-lg">No datasets uploaded yet.</p>
              <p className="text-gray-500">
                Start by uploading your first dataset!
              </p>
            </div>
          ) : (
            <ScrollArea className="h-[400px] w-full rounded-md border border-gray-700 bg-gray-900/50 p-3">
              <div className="space-y-4">
                {datasets.map((dataset) => (
                  <Card
                    key={dataset.id}
                    className="bg-gray-700/50 border-gray-600"
                  >
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="text-xl font-semibold text-blue-300">
                            {dataset.name}
                          </h3>
                          <p className="text-sm text-gray-400">
                            {dataset.description || 'No description provided.'}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              router.push(`/datasets/${dataset.id}`)
                            }
                            className="text-blue-400 border-blue-400 hover:bg-blue-900/30"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteDataset(dataset.id)}
                            className="text-red-400 border-red-400 hover:bg-red-900/30"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm text-gray-400">
                        <p>
                          <strong>Rows:</strong>{' '}
                          {dataset.row_count?.toLocaleString()}
                        </p>
                        <p>
                          <strong>Columns:</strong> {dataset.columns?.length}
                        </p>
                        <p>
                          <strong>Size:</strong>{' '}
                          {formatFileSize(dataset.file_size)}
                        </p>
                        <p>
                          <strong>Uploaded:</strong>{' '}
                          {new Date(dataset.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      {dataset.metadata && (
                        <div className="mt-2">
                          {dataset.metadata.numeric_columns &&
                            dataset.metadata.numeric_columns.length > 0 && (
                              <p className="text-xs text-gray-500">
                                Numeric:{' '}
                                {dataset.metadata.numeric_columns.join(', ')}
                              </p>
                            )}
                          {dataset.metadata.categorical_columns &&
                            dataset.metadata.categorical_columns.length > 0 && (
                              <p className="text-xs text-gray-500">
                                Categorical:{' '}
                                {dataset.metadata.categorical_columns.join(
                                  ', '
                                )}
                              </p>
                            )}
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
