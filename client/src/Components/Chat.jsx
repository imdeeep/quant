import React, { useState, useRef, useEffect } from 'react';
import { ArrowRight, Rocket } from "lucide-react";
import axios from 'axios';
import gsap from 'gsap';
import { TextPlugin } from 'gsap/TextPlugin';

gsap.registerPlugin(TextPlugin);

const LoadingMessage = () => (
    <div className='flex items-start gap-2 hover:bg-zinc-800 rounded p-2'>
        <img
            src="https://website.cdn.speechify.com/2023_10_DALL-E-Logo.webp?quality=80&width=1920"
            alt="ai"
            className='w-8 h-8 rounded border border-zinc-600 flex-shrink-0'
        />
        <div className='flex-1 min-w-0'>
            <div className='flex items-center gap-2'>
                <p className='text-sm font-medium bg-green-500 text-transparent bg-clip-text'>
                    AI gpt-4-mini
                </p>
            </div>
            <div className='mt-1 bg-transparent rounded-md p-2'>
                <div className='animate-pulse flex'>
                    <span className='text-zinc-400 text-sm'>Response generating...</span>
                </div>
            </div>
        </div>
    </div>
);

const Message = ({ message, isLatest }) => {
    const textRef = useRef(null);

    useEffect(() => {
        if (message.type === 'ai' && isLatest && textRef.current) {
            // Clear any existing text first
            textRef.current.textContent = '';
            
            // Split the message into words
            const words = message.content.split(' ');
            let currentText = '';
            
            // Create a GSAP timeline
            const tl = gsap.timeline();
            
            words.forEach((word, index) => {
                tl.to(textRef.current, {
                    duration: 0.2, // Adjust speed as needed
                    text: currentText + word + ' ',
                    ease: "none",
                    onComplete: () => {
                        currentText += word + ' ';
                    }
                });
            });
        }
    }, [message, isLatest]);

    return (
        <div className='flex items-start gap-2 hover:bg-zinc-800 rounded p-2'>
            <img
                src={message.avatar}
                alt={message.type}
                className='w-8 h-8 rounded border border-zinc-600 flex-shrink-0'
            />
            <div className='flex-1 min-w-0'>
                <div className='flex items-center gap-2'>
                    {message.type === 'user' ? (
                        <p className='text-sm font-medium text-purple-400'>User</p>
                    ) : (
                        <p className='text-sm font-medium bg-green-500 text-transparent bg-clip-text'>
                            AI gpt-4-mini
                        </p>
                    )}
                </div>
                <div className={`mt-1 ${message.type === 'ai' ? 'bg-zinc-800/50' : ''} rounded-md p-2`}>
                    {message.type === 'ai' ? (
                        <p ref={textRef} className='text-sm break-words whitespace-pre-wrap min-h-[1.5rem]'></p>
                    ) : (
                        <p className='text-sm break-words whitespace-pre-wrap'>{message.content}</p>
                    )}
                </div>
            </div>
        </div>
    );
};

const Chat = () => {
    const [active, setActive] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleChat = async () => {
        if (!inputText.trim()) return;

        const newUserMessage = {
            type: 'user',
            content: inputText,
            avatar: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRlvA7GIu55Y8DhQqsNrhNa6D6XofSNMrdWWKkBklXoezSPPo5K8aj2-iUwQmmu4Tx91ZA&usqp=CAU"
        };

        setMessages(prev => [...prev, newUserMessage]);
        setActive(true);
        setInputText('');
        setIsLoading(true);

        try {
            const aiResponse = await axios.post('http://localhost:8000/run-flow', {
                message: inputText,
                clear_context: true
            });

            // Make sure we're getting the full response text
            const responseText = aiResponse.data.message?.text || aiResponse.data.message || "Sorry, I couldn't process that.";

            const newAiMessage = {
                type: 'ai',
                content: responseText,
                avatar: "https://website.cdn.speechify.com/2023_10_DALL-E-Logo.webp?quality=80&width=1920"
            };

            setMessages(prev => [...prev, newAiMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage = {
                type: 'ai',
                content: "Sorry, I encountered an error processing your request.",
                avatar: "https://website.cdn.speechify.com/2023_10_DALL-E-Logo.webp?quality=80&width=1920"
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleChat();
        }
    };

    return (
        <div className='w-[45%] bg-[#121212] h-full flex flex-col'>
            <div className='flex-1 p-2 overflow-y-auto'>
                {active && messages.length > 0 ? (
                    <div className="space-y-3">
                        {messages.map((message, index) => (
                            <Message 
                                key={index} 
                                message={message} 
                                isLatest={index === messages.length - 1}
                            />
                        ))}
                        {isLoading && <LoadingMessage />}
                        <div ref={messagesEndRef} />
                    </div>
                ) : (
                    <div className='flex flex-col items-center justify-center h-full'>
                        <Rocket size={50} />
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
                        disabled={isLoading}
                    />
                    <button
                        className="absolute bottom-3 right-2"
                        onClick={handleChat}
                        disabled={!inputText.trim() || isLoading}
                    >
                        <ArrowRight
                            className={`text-black bg-white p-1 rounded ${isLoading ? 'opacity-50' : ''}`}
                            size={25}
                        />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Chat;