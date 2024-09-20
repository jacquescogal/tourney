import React from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null; // Render nothing if the modal is closed

  return (
    <div
      className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg relative"
        onClick={(e) => e.stopPropagation()} // Prevents closing modal when clicking inside it
      >
        <button
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 focus:outline-none"
          onClick={onClose}
        >
          &#10005; {/* X mark for close */}
        </button>
        {children}
      </div>
    </div>
  );
};

export default Modal;