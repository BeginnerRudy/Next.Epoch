'use client';

import Link from 'next/link';
import { Search, Zap, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface HeaderProps {
  onMenuToggle?: () => void;
  isMenuOpen?: boolean;
}

export function Header({ onMenuToggle, isMenuOpen }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim().length >= 2) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="flex items-center justify-between px-4 md:px-6 py-3">
        {/* Mobile menu button */}
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-2 -ml-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
          aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
        >
          {isMenuOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </button>

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <Zap className="w-7 h-7 md:w-8 md:h-8 text-primary-600" />
          <span className="text-lg md:text-xl font-bold text-gray-900">Next.Epoch</span>
        </Link>

        {/* Search Bar - hidden on mobile, shown on larger screens */}
        <form onSubmit={handleSearch} className="hidden md:block flex-1 max-w-xl mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search papers, repos, and more..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </form>

        {/* Right side actions */}
        <div className="flex items-center gap-2 md:gap-4">
          {/* Mobile search link */}
          <Link
            href="/search"
            className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
            aria-label="Search"
          >
            <Search className="w-5 h-5" />
          </Link>
          <Link
            href="/digests"
            className="hidden sm:block text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            Digests
          </Link>
          <div className="hidden md:block h-6 w-px bg-gray-300" />
          <span className="hidden lg:block text-sm text-gray-500">AI Frontier Intelligence</span>
        </div>
      </div>

      {/* Mobile search bar */}
      <div className="md:hidden px-4 pb-3">
        <form onSubmit={handleSearch}>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
            />
          </div>
        </form>
      </div>
    </header>
  );
}
