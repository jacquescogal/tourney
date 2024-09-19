import { CREATE_SESSION, GET_SESSION } from "../api_routes/session";
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

  public static getSession = async (
  ): Promise<Response> => {
    const response = await fetch(GET_SESSION(), {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include"
      });
    return response;
  };

  public static endSession = async (): Promise<Response> => {
    const response = await fetch(GET_SESSION(), {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include"
    });
    return response;
  }
}
export default SessionService;
