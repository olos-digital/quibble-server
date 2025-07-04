'use client'
import { useForm, SubmitHandler } from 'react-hook-form'
import { useRouter } from 'next/navigation'
import AuthCard from '@/components/Auth/AuthCard'
import { Input } from '@/components/Auth/Input'
import { register as registerApi, login as loginApi } from '@/lib/api'

interface FormData {
  username: string;
  email: string;
  dateOfBirth: string;
  password: string;
}

export default function RegisterPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>()

  const router = useRouter()

  const onSubmit: SubmitHandler<FormData> = async data => {
    try {
      await registerApi({
        username: data.username,
        email: data.email,
        dateOfBirth: data.dateOfBirth,
        password: data.password,
      })
      await loginApi(data.username, data.password)
      router.push('/community')
    } catch (e: any) {
      alert(e.message)
    }
  }

  return (
    <AuthCard title="Create account">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Input
          label="Username"
          {...register('username', { required: 'Username is required' })}
          error={errors.username}
        />

        <Input
          label="Email"
          type="email"
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value:
                /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
              message: 'Enter a valid email',
            },
          })}
          error={errors.email}
        />

        <Input
          label="Date of birth"
          type="date"
          {...register('dateOfBirth', {
            required: 'Birth-date is required',
          })}
          error={errors.dateOfBirth}
        />

        <Input
          type="password"
          label="Password"
          {...register('password', {
            required: 'Password is required',
            minLength: { value: 6, message: 'Min 6 chars' },
          })}
          error={errors.password}
        />

        <button
          type="submit"
          className="w-full rounded-md bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating…' : 'Register'}
        </button>

        <p className="pt-2 text-center text-sm text-gray-600">
          Have an account?{' '}
          <a href="/login" className="text-indigo-600 hover:underline">
            Sign in
          </a>
        </p>
      </form>
    </AuthCard>
  )
}
