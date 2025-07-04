'use client'
import { useForm } from 'react-hook-form'
import { useRouter, useSearchParams } from 'next/navigation'
import AuthCard from '@/components/Auth/AuthCard'
import { Input } from '@/components/Auth/Input'
import { login as loginApi } from '@/lib/api'

interface FormData { username: string; password: string }

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>()
  const router = useRouter()
  const params = useSearchParams()
  const callback = params.get('next') || '/community'

  const onSubmit = async (data: FormData) => {
    try {
      const { access_token } = await loginApi(data.username, data.password)
      // Store token – for simplicity in localStorage; replace with cookies or context for production
      localStorage.setItem('token', access_token)
      router.push(callback)
    } catch (e: any) {
      alert(e.message)
    }
  }

  return (
    <AuthCard title="Welcome back">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Input
          label="Username"
          {...register('username', { required: 'Username is required' })}
          error={errors.username}
        />
        <Input
          type="password"
          label="Password"
          {...register('password', { required: 'Password is required' })}
          error={errors.password}
        />
        <button type="submit"
          className="w-full rounded-md bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          disabled={isSubmitting}>
          {isSubmitting ? 'Signing in…' : 'Login'}
        </button>
        <p className="pt-2 text-center text-sm text-gray-600">
          New here? <a href="/register" className="text-indigo-600 hover:underline">Create an account</a>
        </p>
      </form>
    </AuthCard>
  )
}
