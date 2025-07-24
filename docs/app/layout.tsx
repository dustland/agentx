import "./globals.css";
import { Head } from "nextra/components";
import { Layout, Navbar } from "nextra-theme-docs";
import { getPageMap } from "nextra/page-map";
import Image from "next/image";
import TryAppButton from "@/components/app-button";

const navbar = (
  <Navbar
    logo={
      <div>
        <Image
          src={`/logo.png`}
          alt="VibeX"
          height={24}
          width={24}
          style={{
            height: "24px",
            width: "auto",
            display: "inline",
            marginRight: "8px",
          }}
        />
        <b>VibeX</b>
      </div>
    }
    projectLink="https://github.com/dustland/vibex"
  >
    <TryAppButton />
  </Navbar>
);

export const metadata = {
  metadataBase: new URL("https://dustland.github.io/vibex"),
  title: {
    default: "VibeX – Multi-Agent Framework",
    template: "%s | VibeX",
  },
  description:
    "An open-source framework for building, observing, and orchestrating autonomous multi-agent systems.",
  keywords: [
    "VibeX",
    "Multi-Agent",
    "AI",
    "Framework",
    "Autonomous",
    "Python",
    "LLM",
    "Agent Orchestration",
  ],
  applicationName: "VibeX",
  generator: "Next.js",
  appleWebApp: {
    title: "VibeX",
  },
  icons: {
    icon: [
      { url: `/favicon.ico`, sizes: "16x16", type: "image/x-icon" },
      {
        url: `/favicon-16x16.png`,
        sizes: "16x16",
        type: "image/png",
      },
      {
        url: `/favicon-32x32.png`,
        sizes: "32x32",
        type: "image/png",
      },
    ],
    shortcut: `/favicon.ico`,
    apple: `/logo.png`,
  },
  openGraph: {
    url: "https://dustland.github.io/vibex",
    siteName: "VibeX",
    locale: "en_US",
    type: "website",
  },
  other: {
    "msapplication-TileColor": "#fff",
  },
  alternates: {
    canonical: "https://dustland.github.io/vibex",
  },
};

export default async function RootLayout({ children }) {
  const pageMap = await getPageMap();
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <Head />
      <body>
        <Layout
          navbar={navbar}
          editLink="Edit this page on GitHub"
          docsRepositoryBase="https://github.com/dustland/vibex/tree/main/docs"
          sidebar={{ defaultMenuCollapseLevel: 1 }}
          pageMap={pageMap}
        >
          {children}
        </Layout>
      </body>
    </html>
  );
}
