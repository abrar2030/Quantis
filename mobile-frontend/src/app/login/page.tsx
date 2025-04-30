```tsx
'use client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Loader2, LogIn, UserPlus } from 'lucide-react' // Import icons
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert' // Import Alert component

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      // Simulate backend validation
      if (!email || !password) {
        throw new Error('Email and password are required')
      }

      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Store API key and email in localStorage (replace with actual backend response)
      localStorage.setItem('apiKey', 'demo-api-key-12345')
      localStorage.setItem('userEmail', email)

      // Redirect to dashboard after successful login
      router.push('/')
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <Card className="w-full max-w-md bg-gray-800/80 backdrop-blur-sm border border-gray-700 shadow-xl rounded-xl overflow-hidden">
        <CardHeader className="text-center p-6 bg-gray-800/50 border-b border-gray-700">
          <div className="flex justify-center items-center mb-3">
            <LogIn className="h-7 w-7 text-blue-400 mr-2" />
            <CardTitle className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">Quantis Login</CardTitle>
          </div>
          <CardDescription className="text-gray-400">
            Access your prediction dashboard.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleLogin}>
          <CardContent className="p-6 space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-gray-300">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-gray-300">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500 rounded-lg text-lg p-3"
                required
              />
            </div>
            {error && (
              <Alert variant="destructive" className="w-full bg-red-900/30 border-red-700 text-red-300 rounded-lg p-3">
                <AlertDescription className="text-sm">{error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
          <CardFooter className="flex flex-col p-6 bg-gray-800/50 border-t border-gray-700 space-y-4">
            <Button 
              type="submit" 
              className="w-full text-lg font-semibold py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              disabled={isLoading}
            >
              {isLoading ? (
                <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Logging In...</>
              ) : (
                <><LogIn className="mr-2 h-5 w-5" /> Login</>
              )}
            </Button>
            <p className="text-sm text-center text-gray-400 pt-2">
              Don't have an account?{' '}
              <Link href="/register" className="font-medium text-blue-400 hover:text-blue-300 hover:underline flex items-center justify-center mt-1">
                 <UserPlus className="mr-1 h-4 w-4" /> Create Account
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </main>
  )
}
```
