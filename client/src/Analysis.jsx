import React, { useState, useRef, useEffect } from 'react';
import { ArrowRight, Rocket } from "lucide-react";

const Analysis = () => {
  const [active, setActive] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleChat = async () => {
    if (!inputText.trim()) return;

    const newUserMessage = {
      type: 'user',
      content: inputText,
      avatar: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTv8z2UzrkqagcNIknwAwH87o3rThKR0k47kA&s"
    };

    setMessages(prev => [...prev, newUserMessage]);
    setActive(true);
    setInputText('');

    try {
      const aiResponse = {
        type: 'ai',
        content: "Processing your request...",
        avatar: "https://static.vecteezy.com/system/resources/previews/021/059/827/non_2x/chatgpt-logo-chat-gpt-icon-on-white-background-free-vector.jpg"
      };
      
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Chat error:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleChat();
    }
  };

  return (
    <div className='flex h-screen text-white'>
      {/* Left Area */}
      <div className='w-[55%] overflow-y-auto h-full'>
      <div className="absolute top-[-40vh] left-[5vh] z-[-1]">
        <div className="w-[40vw] h-[30vh] bg-purple-400 blur-[8rem] rounded-full"></div>
        <div className="w-[20vw] h-[40vh] bg-blue-400 blur-[10rem] rounded-full"></div>
      </div>
        <div className='logo font-bold italic text-lg py-2 px-4'>Synly</div>
        
        {/* USER DETAILS */}
        <div className='flex items-center gap-2 px-6 py-4 bg-zinc-900/20'>
          <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTv8z2UzrkqagcNIknwAwH87o3rThKR0k47kA&s" alt="" className='w-24 h-24 rounded-full border border-zinc-600' />  
          <div>
            <h1 className='text-xl '>User Name</h1>
            <p className='text-sm text-zinc-500'>Bio</p>
            <div className='space-x-5'><span>100 Follower</span> <span>129 Following</span></div>
          </div>
        </div>

        {/* Aanalysis Graph and Details */}
        <div className='p-2'>
          <h1 className='text-2xl mt-2'>Your Account Insights</h1>
        </div>
      </div>

      {/* Right Area */}
      <div className='w-[45%] bg-[#121212] h-full flex flex-col'>
        <div className='flex-1 p-2 overflow-y-auto'>
          {active && messages.length > 0 ? (
            <div className="space-y-3">
              {messages.map((message, index) => (
                <div key={index} className='flex items-start gap-2 hover:bg-zinc-800 rounded p-2'>
                  <img
                    src={message.avatar}
                    alt={message.type}
                    className='w-8 h-8 rounded border border-zinc-600 flex-shrink-0'
                  />
                  <div className='flex-1 min-w-0'>
                    <p className='text-sm text-purple-400'>
                      {message.type === 'user' ? 'User' : 'AI'}
                      {message.type === 'ai' && <span className='text-xs'> gpt-4o-mini</span>}
                    </p>
                    <p className='text-sm break-words'>{message.content}</p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          ) : (
            <div className='flex flex-col items-center justify-center h-full'>
              <Rocket size={50}/>
              <h1 className='text-xl font-semibold mt-2'>New Chat</h1>
              <p className='text-md text-zinc-500 mt-1'>Start the analysing through chat</p>
            </div>
          )}
        </div>

        <div className='p-2 bg-[#141414] border-t border-zinc-800'>
          <div className='relative'>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              className='w-full h-20 bg-[#0A0A0A] border border-zinc-800 outline-none p-3 rounded-md text-white text-sm resize-none'
              placeholder='Send a message...'
            />
            <button 
              className="absolute bottom-3 right-2" 
              onClick={handleChat}
              disabled={!inputText.trim()}
            >
              <ArrowRight
                className="text-black bg-white p-1 rounded"
                size={25}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analysis;