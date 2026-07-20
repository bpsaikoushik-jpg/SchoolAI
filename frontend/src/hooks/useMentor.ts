import { useMutation } from '@tanstack/react-query';
import { sendMentorChat } from '../services/mentor.service';

export function useMentorChat() {
  return useMutation({
    mutationFn: sendMentorChat,
  });
}
