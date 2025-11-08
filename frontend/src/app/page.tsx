import { ChatWindow } from '@/components/ChatWindow';
import { ConversationSidebar } from '@/components/ConversationSidebar';

export default function Home() {
  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Sidebar - Chat History */}
      <aside className="flex-shrink-0">
        <ConversationSidebar />
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col bg-white min-w-0">
        <ChatWindow />
      </main>
    </div>
  );
}

