'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import {
  LayoutDashboard,
  FileText,
  GitBranch,
  Newspaper,
  Settings,
  Tag,
  Rss,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Papers', href: '/content?type=paper', icon: FileText, queryKey: 'type', queryValue: 'paper' },
  { name: 'Repositories', href: '/content?type=repository', icon: GitBranch, queryKey: 'type', queryValue: 'repository' },
  { name: 'AI News', href: '/content?type=article', icon: Rss, queryKey: 'type', queryValue: 'article' },
  { name: 'Digests', href: '/digests', icon: Newspaper },
  { name: 'Fields', href: '/fields', icon: Tag },
];

// Map field names to arXiv categories for filtering
const fields = [
  { id: 'llm', name: 'Large Language Models', category: 'cs.CL' },
  { id: 'agents', name: 'AI Agents', category: 'cs.AI' },
  { id: 'vision', name: 'Computer Vision', category: 'cs.CV' },
  { id: 'multimodal', name: 'Multimodal AI', category: 'cs.MM' },
  { id: 'robotics', name: 'Robotics', category: 'cs.RO' },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const isActiveLink = (item: typeof navigation[0]) => {
    const basePath = item.href.split('?')[0];

    // For links with query parameters, check both path and query
    if (item.queryKey && item.queryValue) {
      return pathname === basePath && searchParams.get(item.queryKey) === item.queryValue;
    }

    // For simple paths
    if (item.href === '/') {
      return pathname === '/';
    }

    return pathname === basePath || pathname.startsWith(basePath + '/');
  };

  const handleLinkClick = () => {
    // Close mobile menu when a link is clicked
    if (onClose) {
      onClose();
    }
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex-shrink-0 transform transition-transform duration-200 ease-in-out lg:transform-none',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="h-full flex flex-col">
          {/* Mobile header spacer */}
          <div className="lg:hidden h-14" />

          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = isActiveLink(item);

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={handleLinkClick}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                >
                  <item.icon className="w-5 h-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          <div className="px-4 py-2">
            <div className="border-t border-gray-200 pt-4">
              <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Fields
              </h3>
              <div className="space-y-1">
                {fields.map((field) => (
                  <Link
                    key={field.id}
                    href={`/content?category=${field.category}`}
                    onClick={handleLinkClick}
                    className="block px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    {field.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>

          <div className="p-4 border-t border-gray-200 mt-auto">
            <Link
              href="/settings"
              onClick={handleLinkClick}
              className="flex items-center gap-3 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Settings className="w-5 h-5" />
              Settings
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}
