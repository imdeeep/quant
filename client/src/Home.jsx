import React from "react";
import { Link } from "react-router-dom";
import Navbar from "./Components/Navbar";
import { ArrowRight } from "lucide-react";
import { Rocket } from "lucide-react";
import Footer from "./Components/Footer";

const Home = () => {
  return (
    <>
      <Navbar />
      <div className="flex absolute top-[-35vh] z-[-1]">
        <div className="w-[40vw] h-[20vh] bg-blue-400 blur-[8rem] rounded-full"></div>
        <div className="w-[20vw] h-[40vh] bg-blue-400 blur-[10rem] rounded-full"></div>
      </div>

      {/* Notification Button */}
      <div className="flex justify-center">
        <button className="text-zinc-300 hover:bg-zinc-900/40 flex border border-zinc-500 rounded-full py-1 px-4 text-sm items-center bg-transparent gap-2">
          <Rocket size={15} /> Introducing Synly: A new social media analyzer
        </button>
      </div>

      {/* Hero Section */}
      <div className="flex flex-col pt-[5rem] h-[80vh] text-center">
        <h1 className="text-[2.6rem] font-bold text-white mainf">
          Welcome to Synly, let's analyze!
        </h1>
        <p className="text-[1.2rem] text-zinc-400 mainf">
          Unlock actionable insights from your social media platforms.
        </p>
        <div className="mt-6 w-[40vw] h-[30vh] mx-auto relative">
          <Link to="/analysis">
            <ArrowRight
              className="text-black absolute bg-white z-[2] p-1 bottom-2 right-2  rounded"
              size={30}
            />
          </Link>
          <textarea
            name=""
            className="bg-gradient-to-b border w-[40vw] h-[30vh] border-zinc-800 outline-none from-[#141414] to-[#0A0A0A] p-3 rounded-md text-white text-sm resize-none "
            placeholder="Enter your Instagram profile ID -"
            id=""
          ></textarea>
        </div>
      </div>
      <Footer/>
    </>
  );
};

export default Home;
