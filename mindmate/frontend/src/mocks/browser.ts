import { setupWorker } from "msw/browser";

import { handlers } from "./handlers";

// Browser (dev) request interception. Started only in dev from main.tsx.
export const worker = setupWorker(...handlers);