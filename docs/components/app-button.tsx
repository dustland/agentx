"use client";

import React from "react";
import Image from "next/image";
import { Link } from "nextra-theme-docs";

export default function TryAppButton() {
  return (
    <Link
      href="https://app.vibex.co"
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center rounded-md gap-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 py-1.5 px-3 transition-colors"
    >
      <Image
        src="/logo.png"
        alt="VibeX"
        width={14}
        height={14}
        style={{ objectFit: "contain" }}
      />
      <span className="font-semibold">VibeX Now!</span>
    </Link>
  );
}
