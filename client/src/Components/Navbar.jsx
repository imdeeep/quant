import React from 'react'
import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <div className='bg-transparent flex justify-between py-2 px-4 text-white items-center'>
        <Link to="/" className='logo font-bold italic text-[1.2rem]'>Synly</Link>
        <div className='space-x-2'>
          <a href="/" className='text-sm bg-zinc-800 hover:bg-zinc-900 px-2 py-1  rounded-md'>History</a>
        <Link to="/analysis" className='text-sm bg-blue-500 hover:bg-blue-600 px-2 py-1  rounded-md'>Try Now</Link>
        </div>
    </div>
  )
}

export default Navbar