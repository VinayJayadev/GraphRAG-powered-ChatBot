import { ChatWindow } from '@/components/ChatWindow';
import { ConversationSidebar } from '@/components/ConversationSidebar';

export default function Home() {
  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Sidebar */}
      <ConversationSidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white">
        <ChatWindow />
      </div>
    </div>
  );
}

