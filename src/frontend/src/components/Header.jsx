import React from 'react';
import { PanelLeftClose } from 'lucide-react';

const Header = () => {
  return (
    <div className="flex items-center gap-4 px-5 py-3 border-b border-gray-200 bg-white shadow-sm shrink-0 z-10 w-full top-0">
      <PanelLeftClose className="w-5 h-5 text-gray-700 hover:text-gray-900 cursor-pointer" />
      <div className="flex items-center gap-2 text-[15px]">
        <span className="text-gray-400 font-medium tracking-wide">Mapping</span>
        <span className="text-gray-300">/</span>
        <span className="font-semibold text-gray-900 tracking-wide">Order to Cash</span>
      </div>
    </div>
  );
};

export default Header;
