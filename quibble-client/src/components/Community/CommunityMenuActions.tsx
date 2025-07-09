'use client'

import { useEffect, useRef, useState } from 'react'
import Image from 'next/image'

interface Action {
  label: string
  src: string
  alt: string
}

/* icons stored in /public/assets/images */
const ACTIONS: Action[] = [
  { label: 'Automate', src: '/assets/images/Automate_Icon.png', alt: 'Automate' },
  { label: 'Create',   src: '/assets/images/Quibble_Head.png',  alt: 'Create'   },
  { label: 'Connect',  src: '/assets/images/Social_Logos.png',  alt: 'Connect'  },
]

export default function CommunityMenuActions() {
  const btnRefs  = useRef<HTMLButtonElement[]>([])
  const [ringPos, setRingPos]   = useState({ left: 0, width: 0 })
  const [active,  setActive]    = useState(1)           // 1 = “Create” by default

  const moveToIdx = (idx: number) => {
    const el = btnRefs.current[idx]
    if (!el) return
    setRingPos({ left: el.offsetLeft, width: el.offsetWidth })
    setActive(idx)
  }

  const resetToDefault = () => moveToIdx(1)

  /* centre ring on first paint */
  useEffect(resetToDefault, [])


  return (
    <div className="relative rounded-2xl isolate flex flex-col px-8 py-6 m-4">

      {/* background banner */}
      <Image
        src="/assets/images/Community_Header.png"
        alt=""
        fill
        priority
        className="object-fit w-full h-full pointer-events-none select-none z-10"
      />

      <div className="flex flex-col items-start z-20 gap-2 text-white m-5">
        <h3 className="uppercase font-bold text-2xl">Create. Engage. Grow.</h3>
        Everything you need to <br /> share your ideas.
      </div>

      {/* action buttons */}
      <div className="relative z-30 mx-auto flex items-center gap-4 bg-gray-200 p-1 rounded-full border-2 border-indigo-500 shadow-lg translate-y-12">

        <span
          className="absolute top-0 h-full rounded-full bg-indigo-500 ring-4 ring-indigo-500 transition-all duration-300 pointer-events-none"
          style={{ left: ringPos.left, width: ringPos.width }}
        />

        {ACTIONS.map(({ label, src, alt }, idx) => (
          <button
            key={label}
            ref={el => { if (el) btnRefs.current[idx] = el }}
            onMouseEnter={() => moveToIdx(idx)}
            onMouseLeave={resetToDefault}
            className={`relative z-50 flex flex-col items-center gap-1 rounded-full px-6 py-3 font-semibold uppercase transition-colors
              ${idx === active ? 'text-white' : 'text-gray-900'}`}
          >
            <Image src={src} alt={alt} width={48} height={48} className="h-12 w-12" />
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}
