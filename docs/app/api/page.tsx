'use client'

import { ApiDoc } from "../../components/api-doc";
import { useEffect } from 'react';

export default function ApiPage() {
  useEffect(() => {
    // Add custom styles for API page layout
    const style = document.createElement('style');
    style.textContent = `
      /* Hide sidebar and toc for API page */
      .nextra-sidebar-container,
      .nextra-toc {
        display: none !important;
      }
      
      /* Make main content full width */
      main {
        max-width: 100% !important;
      }
      
      /* Full height article */
      article {
        padding: 0 !important;
        max-width: 100% !important;
        min-height: calc(100vh - 64px) !important;
        position: relative;
        display: flex;
        flex-direction: column;
      }
      
      /* Make the API doc container fill the available space */
      article > * {
        flex: 1;
        display: flex;
        flex-direction: column;
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return <ApiDoc />;
}
