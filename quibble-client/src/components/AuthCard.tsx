import type { ReactNode } from 'react'

export default function AuthCard({ children, title }: { children: ReactNode; title: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-50 to-indigo-100">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-lg">
        <h1 className="mb-6 text-center text-2xl font-semibold text-gray-800">{title}</h1>
        {children}
      </div>
    </div>
  )
}
