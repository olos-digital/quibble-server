import { FaUserCircle, FaHeart, FaMagic, FaCrown, FaKey, FaBell, FaCog } from 'react-icons/fa'
import { MdPostAdd, MdDashboard } from 'react-icons/md'
import Link from 'next/link'

export default function CommunitySidebar() {
  return (
    <aside className="w-72 bg-white shadow flex flex-col gap-2 p-6 min-h-screen sticky">
      <div className="flex flex-col items-center mb-6">
        <FaUserCircle className="text-5xl text-indigo-400 mb-2" />
        <span className="font-bold text-md">user1234</span>
        <button className="text-xs text-indigo-600 hover:underline mt-1">Edit Profile</button>
      </div>
      <nav className="flex flex-col gap-2 text-gray-700">
        <SidebarLink icon={<FaHeart />} text="Liked Posts" />
        <SidebarLink icon={<MdPostAdd />} text="Create Post" />
        <SidebarLink icon={<FaMagic />} text="Automate" />
        <SidebarLink icon={<FaCrown />} text="Advanced Plans" />
        <SidebarLink icon={<FaKey />} text="API Keys" />
        <SidebarLink icon={<FaBell />} text="Latest Updates" />
        <SidebarLink icon={<MdDashboard />} text="Dashboard" />
        <SidebarLink icon={<FaCog />} text="Settings" />
      </nav>
    </aside>
  )
}

function SidebarLink({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <Link href="#" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-indigo-50 transition">
      <span className="text-lg">{icon}</span>
      <span className="font-medium">{text}</span>
    </Link>
  )
}
