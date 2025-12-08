"use client";

import { useEffect, useState, useCallback } from 'react';
import { useUser, useAuth } from '@clerk/nextjs';
import { User, getCurrentUser, syncUser } from '@/lib/auth';

export function useCurrentUser() {
  const { user: clerkUser, isLoaded: clerkLoaded } = useUser();
  const { getToken } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadUser = useCallback(async () => {
    if (!clerkLoaded) {
      return;
    }

    if (!clerkUser) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const token = await getToken();

      if (!token) {
        setLoading(false);
        setError('No authentication token');
        return;
      }

      // First, sync user to backend (this creates user if doesn't exist)
      try {
        await syncUser(
          clerkUser.id,
          clerkUser.emailAddresses[0]?.emailAddress || '',
          clerkUser.fullName || null,
          token
        );
      } catch (syncError) {
        console.warn('Failed to sync user:', syncError);
        // Continue anyway - user might already exist
      }

      // Then get current user info including role
      try {
        const userData = await getCurrentUser(token);
        setUser(userData);
        setError(null);
      } catch (getError) {
        console.error('Failed to get user:', getError);
        // If getCurrentUser fails, user might not exist yet - that's ok
        // Set user to null but don't set error (will show onboarding)
        setUser(null);
        setError(null);
      }
    } catch (err) {
      console.error('Failed to load user:', err);
      setError(err instanceof Error ? err.message : 'Failed to load user');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [clerkUser, clerkLoaded, getToken]);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  return {
    user,
    role: user?.role || null,
    loading: loading || !clerkLoaded,
    error,
    refetch: loadUser
  };
}

