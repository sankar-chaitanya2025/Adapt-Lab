import { useState, useCallback } from 'react';
import client from '../api/client';

export function useSession() {
  const [currentProblem, setCurrentProblem] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [socraticHint, setSocraticHint] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const startSession = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setSubmissionResult(null);
    setSocraticHint(null);
    try {
      const res = await client.post('/session/start');
      setSessionId(res.data.session_id);
      setCurrentProblem(res.data.problem);
      return res.data;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to start session';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const submitCode = useCallback(async (sId, sourceCode) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await client.post(`/session/${sId}/submit`, {
        source_code: sourceCode,
      });
      setSubmissionResult(res.data);
      if (res.data.hint) {
        setSocraticHint(res.data.hint);
      }
      return res.data;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Submission failed';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const nextProblem = useCallback(async () => {
    setSubmissionResult(null);
    setSocraticHint(null);
    return startSession();
  }, [startSession]);

  const clearError = useCallback(() => setError(null), []);

  return {
    currentProblem,
    sessionId,
    submissionResult,
    socraticHint,
    isLoading,
    error,
    startSession,
    submitCode,
    nextProblem,
    clearError,
  };
}

export default useSession;
