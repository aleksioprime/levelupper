import { UserResource } from "./user.resource";
import { AuthResource } from "./auth.resource";

export default {
    user: new UserResource(),
    auth: new AuthResource(),
};