import Link from 'next/link';
import Image from 'next/image';

import { FaUser } from 'react-icons/fa';
import { MdEdit } from 'react-icons/md';

export default function IntroHeader() {
  return (
    <header className="flex justify-between items-center px-12 py-6">
    <Image src="/assets/images/logo.png" alt="Logo" width={220} height={190} className="pl-8"/>
      <div className="flex gap-8 items-center">
        <Link href="/profile" className="font-bold flex items-center gap-1 text-black">
          <span className="material-icons text-lg text-indigo-500 mr-2">
            <FaUser size={18}/>
          </span> 
          Profile
        </Link>
        <Link href="/create" className="rounded-full bg-indigo-500 px-4 py-2 text-white font-bold shadow hover:bg-indigo-600 transition flex align-middle gap-2">
          CREATE 
          <span className="material-icons align-middle ml-1">
            <img src="assets/icons/action.svg" alt="Action" width={24} height={24} />
          </span>
        </Link>
      </div>
    </header>
  )
}
