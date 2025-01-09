import React from 'react'

const Loader = () => {
  return (
    
    <div className='flex justify-center w-full fixed top-0 left-0 bg-blue-100 opacity-50 z-50 items-center min-h-screen'>
        <div className='w-16 h-16 border-4 border-t-4 border-blue-500 border-t-blue-500 rounded-full animate-spin'></div>
    </div>
  )
}

export default Loader