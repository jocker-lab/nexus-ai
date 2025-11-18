'use client';

import { useEffect, useRef } from 'react';

export interface InputEnhancement {
  id: string;
  icon: React.ReactNode;
  label: string;
  enabled: boolean;
  onChange: (enabled: boolean) => void;
}

interface InputEnhancementsMenuProps {
  x: number;
  y: number;
  enhancements: InputEnhancement[];
  onClose: () => void;
}

export function InputEnhancementsMenu({ x, y, enhancements, onClose }: InputEnhancementsMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 点击外部关闭菜单
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    // ESC键关闭菜单
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  return (
    <div
      ref={menuRef}
      className="fixed z-50 bg-[#2a2a2a] rounded-xl shadow-xl border border-[#3a3a3a] py-2 min-w-[240px]"
      style={{
        left: `${x}px`,
        bottom: `${window.innerHeight - y + 10}px`,
      }}
    >
      {enhancements.map((enhancement) => (
        <div
          key={enhancement.id}
          className="flex items-center justify-between px-4 py-3 hover:bg-[#3a3a3a] transition-colors cursor-pointer"
          onClick={() => enhancement.onChange(!enhancement.enabled)}
        >
          <div className="flex items-center gap-3">
            <span className="w-5 h-5 flex items-center justify-center text-[#9ca3af]">
              {enhancement.icon}
            </span>
            <span className="text-sm text-[#e0e0e0]">{enhancement.label}</span>
          </div>
          <div
            className={`relative w-10 h-5 rounded-full transition-colors ${
              enhancement.enabled ? 'bg-[#3b82f6]' : 'bg-[#4a4a4a]'
            }`}
          >
            <div
              className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
                enhancement.enabled ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </div>
        </div>
      ))}
      <div className="px-4 py-2 text-[11px] text-[#6b7280] border-t border-[#3a3a3a] mt-2">
        提示：回车发送，Shift+回车换行
      </div>
    </div>
  );
}
