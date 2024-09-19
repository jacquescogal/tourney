import { CREATE_SESSION } from "../api_routes/session";
import { UserLoginRequest } from "../types/user";

class SessionService {
  public static createSession = async (
    payload: UserLoginRequest
  ): Promise<Response> => {
    const response = await fetch(CREATE_SESSION(), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      credentials: "include"
    });
    return response;
  };
}
export default SessionService;
