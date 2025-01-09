import React from 'react';
import { FaLinkedinIn } from "react-icons/fa";
import { Link } from 'react-router-dom'
import { useTheme } from './context/ThemeContext'


const About = () => {
  const { theme } = useTheme()
  const teamMembers = [
    {
      name: "Akash Bais",
      role: "Backend Developer",
      image: "https://res.cloudinary.com/dikkjtvur/image/upload/v1736442574/1732695497391_mre2nq.jpg",
      linkedin: "https://www.linkedin.com/in/bais-akash/"
    },
    {
      name: "Devang Sharma",
      role: "Research",
      image: "https://i.ibb.co/6bw587V/Picsart-24-06-17-20-23-29-600.jpg",
      linkedin: "https://www.linkedin.com/in/devang-sharma-88aa84288"
    },
    {
      name: "Mandeep Yadav",
      role: "Full Stack Developer",
      image: "https://mandeepyadav.vercel.app/me.jpg",
      linkedin: "https://www.linkedin.com/in/mandeepyadav27/"
    },
    {
      name: "Nawadha Jadiya",
      role: "Langflow and Prompting",
      image: "https://res.cloudinary.com/dikkjtvur/image/upload/v1736441788/WhatsApp_Image_2025-01-09_at_10.26.01_PM_luhvhr.jpg",
      linkedin: "https://www.linkedin.com/in/nawadha-jadiya-aab426253/"
    },
    {
      name: "Sneha Yadav",
      role: "UI and Design",
      image: "https://res.cloudinary.com/dikkjtvur/image/upload/v1736442411/WhatsApp_Image_2025-01-09_at_10.34.44_PM_ypc2o3.jpg",
      linkedin: "https://www.linkedin.com/in/sneha-yadav-02909021b/"
    }
  ];

  return (
    <>
     
    <div className="min-h-screen dark-transition mainf">
    <div className={`bg-transparent flex justify-between py-2 px-4 items-center ${
      theme === 'dark' ? 'text-white' : 'text-gray-900'
    }`}>
      <Link to="/" className='logo font-bold italic text-[1.2rem]'>Synly</Link>
      <div className='flex items-center space-x-4'>
        <div className='space-x-2'>
          <Link to="/about" className={`text-sm ${
            theme === 'dark' 
            ? 'bg-zinc-800 hover:bg-zinc-700' 
            : 'bg-gray-200 hover:bg-gray-300'
          } px-2 py-1 rounded-md`}>
            About
          </Link>
          <Link to="/analysis" className='text-sm bg-blue-500 hover:bg-blue-600 px-2 py-1 rounded-md text-white'>
            Analysis
          </Link>
        </div>
      </div>
    </div>
      {/* Enhanced Header Section */}
      <div className="text-center py-20 px-4 ">
        <div className="relative inline-block">
          <h1 className="text-4xl  md:text-6xl font-bold mb-4 relative">
            <span className="absolute -top-8 left-1/2 -tra  nslate-x-1/2 text-sm opacity-70 font-mono text-blue-500 animate-pulse">&lt;team&gt;</span>
            Meet Our Team
            <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-sm opacity-70 font-mono text-blue-500 animate-pulse">&lt;/team&gt;</span>
          </h1>
        </div>
        <p className="mt-12 text-xl opacity-90 font-mono bg-gradient-to-r from-blue-500 to-purple-500 text-transparent bg-clip-text">
          Building the future with code, one line at a time
        </p>
      </div>

      {/* Enhanced Team Container */}
      <div className="max-w-7xl mx-auto flex flex-wrap justify-center gap-8 px-4 pb-20">
        {teamMembers.map((member, index) => (
          <div 
            key={index}
            className="w-[320px] text-center p-8 rounded-2xl bg-[var(--card-bg)] border border-[var(--border-color)]
                     hover:-translate-y-2 transition-transform duration-300 ease-out group
                     hover:shadow-xl hover:shadow-blue-500/10 relative overflow-hidden"
            style={{
              animation: `fadeInUp 0.6s ease forwards ${index * 0.2}s`,
              opacity: 0
            }}
          >
            {/* Decorative Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
              <div className="absolute top-0 left-0 w-20 h-20 border-t-2 border-l-2 border-blue-500 transition-all duration-300 group-hover:w-24 group-hover:h-24"></div>
              <div className="absolute bottom-0 right-0 w-20 h-20 border-b-2 border-r-2 border-blue-500 transition-all duration-300 group-hover:w-24 group-hover:h-24"></div>
            </div>

            {/* Profile Image Container */}
            <div className="relative mb-8">
              <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-lg transform scale-95 group-hover:scale-105 transition-transform duration-300 ease-out"></div>
              <div className="relative w-[220px] h-[220px] mx-auto">
                <img 
                  src={member.image} 
                  alt={member.name}
                  className="w-full h-full rounded-full object-cover transition-all duration-300 ease-out
                           group-hover:rounded-2xl border-4 border-blue-500/30 group-hover:border-blue-500/50"
                />
              </div>
              
              {/* Enhanced LinkedIn Icon */}
              <a 
                href={member.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-[40px] h-[40px] bg-blue-500 rounded-full 
                         hover:scale-110 transition-all duration-200 ease-out shadow-lg hover:shadow-blue-500/50
                         hover:bg-blue-600 flex items-center justify-center"
              >
                <FaLinkedinIn 
                  size={22} 
                  className="text-white" 
                />
              </a>
            </div>

            {/* Enhanced Name Box */}
            <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 dark:from-blue-500/20 dark:to-purple-500/20 
                          text-blue-600 dark:text-blue-400 py-3 px-6 rounded-xl 
                          mx-auto max-w-[90%] text-xl font-semibold mb-4 backdrop-blur-sm
                          transition-all duration-300 ease-out group-hover:from-blue-500/20 group-hover:to-purple-500/20">
              {member.name}
            </div>

            {/* Enhanced Role */}
            <div className="text-md opacity-85 px-4 py-2 rounded-lg inline-block 
                          before:content-['<'] after:content-['/>''] 
                          before:text-blue-500 after:text-blue-500
                          before:mr-2 after:ml-2
                          bg-blue-500/5 hover:bg-blue-500/10 transition-colors duration-200 ease-out">
              {member.role}
            </div>
          </div>
        ))}
      </div>
    </div>
    </>
  );
};

export default About;