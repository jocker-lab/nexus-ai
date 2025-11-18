'use client';

import { useState, useEffect, useRef } from 'react';

interface RenameDialogProps {
  initialTitle: string;
  onConfirm: (newTitle: string) => void;
  onCancel: () => void;
}

export function RenameDialog({ initialTitle, onConfirm, onCancel }: RenameDialogProps) {
  const [title, setTitle] = useState(initialTitle);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // 自动聚焦并选中文本
    if (inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }

    // ESC键取消
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onCancel();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onCancel]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onConfirm(title.trim());
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-[#2a2a2a] rounded-lg shadow-xl border border-[#3a3a3a] w-full max-w-md p-6">
        <h3 className="text-lg font-semibold text-[#e0e0e0] mb-4">重命名对话</h3>
        <form onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 bg-[#212121] border border-[#3a3a3a] rounded-md text-[#e0e0e0] text-sm focus:outline-none focus:border-[#3b82f6]"
            placeholder="输入新标题"
          />
          <div className="flex justify-end gap-2 mt-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm text-[#9ca3af] hover:text-[#e0e0e0] transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm bg-[#3b82f6] text-white rounded-md hover:bg-[#2563eb] transition-colors"
            >
              确认
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
