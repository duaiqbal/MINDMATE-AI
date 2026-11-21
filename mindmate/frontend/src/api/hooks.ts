import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "./client";
import type {
  ChatReply,
  CrisisResources,
  MemoryList,
  MoodTrends,
} from "./types";

export function useMoodTrends() {
  return useQuery({
    queryKey: ["mood", "trends"],
    queryFn: () => api.get<MoodTrends>("/v1/mood/trends"),
  });
}

export function useLogMood() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (mood: number) => api.post("/v1/mood", { mood }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mood", "trends"] }),
  });
}

export function useMemory() {
  return useQuery({
    queryKey: ["memory"],
    queryFn: () => api.get<MemoryList>("/v1/memory"),
  });
}

export function useDeleteMemory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.del(`/v1/memory/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memory"] }),
  });
}

export function useSendChat() {
  return useMutation({
    mutationFn: (message: string) =>
      api.post<ChatReply>("/v1/chat", { message }),
  });
}

export function useCrisisResources() {
  return useQuery({
    queryKey: ["crisis-resources"],
    queryFn: () => api.get<CrisisResources>("/v1/crisis-resources"),
  });
}