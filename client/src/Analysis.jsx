import React, { useState, useRef, useEffect } from 'react';
import Loader from './Components/Loader';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import InstagramProfile from './Components/InstagramProfile';
import { Link } from 'react-router-dom';
import { data } from './Components/data';
import Chat from './Components/Chat';

const Analysis = () => {

  const location = useLocation();
  // const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const queryParams = new URLSearchParams(location.search);
  const uname = queryParams.get('uname');

  // console.log(data)

  // Account related Code
  // useEffect(() => {
  //   const postData = async () => {
  //     setIsLoading(false);
  //     try {
  //       const response = await axios.post('http://localhost:8000/scrape-instagram', {
  //         username: uname,
  //         results_limit: 25
  //       });
  //       console.log(response.data);
  //       setData(response.data);
  //     } catch (err) {
  //       setError(err);
  //       console.log(err);
  //     } finally {
  //       setIsLoading(false);
  //     }
  //   };
  //   postData();
  // }, [uname])

  return (
    <>
      {isLoading && <Loader />}
      <div className='flex h-screen text-white'>
        {/* Left Area */}
        <div className='w-[55%] overflow-y-auto h-full'>
          <div className="absolute top-[-40vh] left-[5vh] z-[-1]">
            <div className="w-[40vw] h-[30vh] bg-purple-400 blur-[8rem] rounded-full"></div>
            <div className="w-[20vw] h-[40vh] bg-blue-400 blur-[10rem] rounded-full"></div>
          </div>
          <div className='py-2 px-4'>
            <Link to="/" className='logo font-bold italic text-[1.2rem]'>Synly</Link>
          </div>
          {data && <InstagramProfile data={data} />}
        </div>

        {/* Right Area */}
        <Chat />
      </div>
    </>
  );
};

export default Analysis;