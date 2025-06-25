'use client';

import React from 'react';
import APITestSuite from '@/components/testing/APITestSuite';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

export default function TestingPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <APITestSuite />
      </div>
    </DashboardLayout>
  );
} 