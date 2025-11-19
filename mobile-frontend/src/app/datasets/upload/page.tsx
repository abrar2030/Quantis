import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, UploadCloud, FileText, CheckCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
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

export default function DatasetUpload() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [uploadState, setUploadState] = useState({
    file: null as File | null,
    name: '',
    description: '',
    isUploading: false,
    uploadProgress: 0,
    error: null as string | null,
    success: false,
    uploadedDataset: null as Dataset | null,
    preview: null as any | null,
  });

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      setUploadState(prev => ({
        ...prev,
        error: 'Invalid file type. Please upload CSV, JSON, or Excel files.',
      }));
      return;
    }

    const file = acceptedFiles[0];
    if (file) {
      setUploadState(prev => ({
        ...prev,
        file,
        name: file.name.replace(/\.[^/.]+$/, ''), // Remove extension
        error: null,
        success: false,
      }));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const handleUpload = async () => {
    if (!uploadState.file || !uploadState.name.trim()) {
      setUploadState(prev => ({
        ...prev,
        error: 'Please select a file and provide a name.',
      }));
      return;
    }

    setUploadState(prev => ({
      ...prev,
      isUploading: true,
      uploadProgress: 0,
      error: null,
    }));

    try {
      const formData = new FormData();
      formData.append('file', uploadState.file);
      formData.append('name', uploadState.name);
      formData.append('description', uploadState.description);

      const response = await datasetsAPI.uploadDataset(
        formData,
        (progressEvent: any) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadState(prev => ({
            ...prev,
            uploadProgress: progress,
          }));
        }
      );

      const previewResponse = await datasetsAPI.getDatasetPreview(response.id, 5);

      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        success: true,
        uploadedDataset: response,
        preview: previewResponse,
      }));
    } catch (error: any) {
      const apiError = handleApiError(error);
      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        error: apiError.message,
      }));
    }
  };

  const handleReset = () => {
    setUploadState({
      file: null,
      name: '',
      description: '',
      isUploading: false,
      uploadProgress: 0,
      error: null,
      success: false,
      uploadedDataset: null,
      preview: null,
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (authLoading || !user) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <Loader2 className="h-12 w-12 animate-spin text-blue-400 mb-4" />
        <p className="text-lg text-gray-300">Loading...</p>
      </main>
    );
  }

  if (uploadState.success && uploadState.uploadedDataset) {
    return (
      <main className="flex min-h-screen flex-col items-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <Card className="w-full max-w-3xl bg-gray-800/80 backdrop-blur-sm border border-gray-700 shadow-xl rounded-xl overflow-hidden">
          <CardHeader className="text-center p-6 bg-gray-800/50 border-b border-gray-700">
            <CheckCircle className="mx-auto h-16 w-16 text-green-400 mb-3" />
            <CardTitle className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-teal-500">
              Dataset Uploaded Successfully!
            </CardTitle>
            <CardDescription className="text-gray-400">
              Your dataset "{uploadState.uploadedDataset.name}" has been processed and is ready to use.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-300 mb-2">Dataset Information</h3>
                <p className="text-gray-400"><strong>Name:</strong> {uploadState.uploadedDataset.name}</p>
                <p className="text-gray-400"><strong>Rows:</strong> {uploadState.uploadedDataset.row_count?.toLocaleString()}</p>
                <p className="text-gray-400"><strong>Columns:</strong> {uploadState.uploadedDataset.columns?.length}</p>
                <p className="text-gray-400"><strong>File Size:</strong> {formatFileSize(uploadState.uploadedDataset.file_size)}</p>
              </div>
              {uploadState.uploadedDataset.metadata && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-300 mb-2">Column Types</h3>
                  {uploadState.uploadedDataset.metadata.numeric_columns && uploadState.uploadedDataset.metadata.numeric_columns.length > 0 && (
                    <p className="text-gray-400"><strong>Numeric:</strong> {uploadState.uploadedDataset.metadata.numeric_columns.join(', ')}</p>
                  )}
                  {uploadState.uploadedDataset.metadata.categorical_columns && uploadState.uploadedDataset.metadata.categorical_columns.length > 0 && (
                    <p className="text-gray-400"><strong>Categorical:</strong> {uploadState.uploadedDataset.metadata.categorical_columns.join(', ')}</p>
                  )}
                </div>
              )}
            </div>

            {uploadState.preview && (
              <div className="mt-6">
                <h3 className="text-xl font-semibold text-gray-300 mb-2">Data Preview</h3>
                <div className="overflow-x-auto rounded-md border border-gray-700 bg-gray-900/50">
                  <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-800">
                      <tr>
                        {uploadState.preview.columns.map((column: string) => (
                          <th key={column} scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {uploadState.preview.data.map((row: any, index: number) => (
                        <tr key={index}>
                          {uploadState.preview.columns.map((column: string) => (
                            <td key={column} className="px-4 py-2 whitespace-nowrap text-sm text-gray-400">
                              {row[column]?.toString() || ''}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex flex-col sm:flex-row justify-center p-6 bg-gray-800/50 border-t border-gray-700 space-y-3 sm:space-y-0 sm:space-x-4">
            <Button
              onClick={handleReset}
              className="w-full sm:w-auto text-lg font-semibold py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-300 ease-in-out"
            >
              Upload Another Dataset
            </Button>
            <Button
              variant="outline"
              onClick={() => router.push('/datasets')}
              className="w-full sm:w-auto text-lg font-semibold py-3 rounded-lg bg-transparent border-gray-600 hover:bg-gray-700/50 text-gray-300 hover:text-white"
            >
              View All Datasets
            </Button>
          </CardFooter>
        </Card>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <Card className="w-full max-w-3xl bg-gray-800/80 backdrop-blur-sm border border-gray-700 shadow-xl rounded-xl overflow-hidden">
        <CardHeader className="text-center p-6 bg-gray-800/50 border-b border-gray-700">
          <CardTitle className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Upload New Dataset
          </CardTitle>
          <CardDescription className="text-gray-400">
            Upload your dataset to start building machine learning models.
            Supported formats: CSV, JSON, Excel (.xlsx, .xls)
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          {uploadState.error && (
            <Alert
              variant="destructive"
              className="w-full bg-red-900/30 border-red-700 text-red-300 rounded-lg"
            >
              <AlertTitle className="font-semibold">Error</AlertTitle>
              <AlertDescription>{uploadState.error}</AlertDescription>
            </Alert>
          )}

          <div
            {...getRootProps()}
            className={`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg text-center transition-colors duration-200
              ${isDragActive
                ? 'border-blue-500 bg-gray-700/30'
                : 'border-gray-600 bg-gray-800/50 hover:border-blue-500'}
            `}
          >
            <input {...getInputProps()} />
            <UploadCloud className="h-16 w-16 text-gray-400 mb-4" />
            <p className="text-lg font-semibold text-gray-300">
              {isDragActive
                ? 'Drop the file here...' : 'Drag & drop a file here, or click to select'}
            </p>
            <p className="text-sm text-gray-500">Maximum file size: 10MB</p>
          </div>

          {uploadState.file && (
            <div className="flex items-center space-x-3 p-3 rounded-md bg-gray-700/50 border border-gray-600">
              <FileText className="h-6 w-6 text-blue-400" />
              <div className="flex-grow">
                <p className="text-gray-300 font-medium">{uploadState.file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(uploadState.file.size)}</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="dataset-name" className="text-sm font-medium text-gray-300">Dataset Name</Label>
              <Input
                id="dataset-name"
                placeholder="My New Dataset"
                value={uploadState.name}
                onChange={(e) => setUploadState(prev => ({ ...prev, name: e.target.value }))}
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3"
                disabled={uploadState.isUploading}
              />
            </div>
            <div>
              <Label htmlFor="description" className="text-sm font-medium text-gray-300">Description (Optional)</Label>
              <Input
                id="description"
                placeholder="A brief description of my dataset"
                value={uploadState.description}
                onChange={(e) => setUploadState(prev => ({ ...prev, description: e.target.value }))}
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3"
                disabled={uploadState.isUploading}
              />
            </div>
          </div>

          {uploadState.isUploading && (
            <div className="space-y-2">
              <p className="text-gray-300">Uploading... {uploadState.uploadProgress}%</p>
              <Progress value={uploadState.uploadProgress} className="w-full" />
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-center p-6 bg-gray-800/50 border-t border-gray-700">
          <Button
            onClick={handleUpload}
            disabled={!uploadState.file || !uploadState.name.trim() || uploadState.isUploading}
            className="w-full sm:w-auto text-lg font-semibold py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {uploadState.isUploading ? (
              <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Uploading...</>
            ) : (
              <><UploadCloud className="mr-2 h-5 w-5" /> Upload Dataset</>
            )}
          </Button>
        </CardFooter>
      </Card>
    </main>
  );
}
