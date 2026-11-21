import { setupServer } from "msw/node";

import { handlers } from "./handlers";

// Node (test) request interception.
export const server = setupServer(...handlers);