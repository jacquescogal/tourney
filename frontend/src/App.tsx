import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Header from "./components/commons/Header";
import TeamDetailPage from "./pages/team_detail_page/TeamDetailPage";
import CreateTeamPage from "./pages/admin/CreateTeamPage";
import CreateMatchupPage from "./pages/admin/CreateMatchupPage";
import LoginPage from "./pages/login/LoginPage";
import { IUserSession } from "./types/session";
import SessionService from "./api/SessionService";
import AdminPanel from "./pages/admin/HomePage";
import LeaderboardPage from "./pages/leaderboard/LeaderboardPage";

function App() {
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [teamID, setTeamID] = useState<number>(0);
  const [userSession, setUserSession] = React.useState<IUserSession | null>(null);

  useEffect(()=>{
    const fetchSession = async ()=>{
    const response = await SessionService.getSession();
    if (response.ok){
      const session = await response.json();
      setUserSession(session);
      sessionStorage.setItem("session", JSON.stringify(session));
    }
    else{
      setUserSession(null);
    }
  }
  fetchSession();
  },[])

  const endSession = async ()=>{
    const response = await SessionService.endSession();
    if (response.ok){
      setUserSession(null);
      sessionStorage.clear();
    }
  }
  return (
    <Router>
      {/* Header banner */}
      <Header userSession={userSession} endSession={endSession}/>
      {/* Routes to pages */}
      <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/admin" element={<AdminPanel modalOpen={modalOpen} setModalOpen={setModalOpen}
        teamID={teamID} setTeamID={setTeamID}/>}>
          <Route
            path="team"
            element={<CreateTeamPage setModalOpen={setModalOpen} setTeamID={setTeamID}/>}
          />
          <Route
            path="matchup"
            element={<CreateMatchupPage setModalOpen={setModalOpen} setTeamID={setTeamID}/>}
          />
        </Route>
        <Route path="/login" element={<LoginPage setUserSession={setUserSession}/>} />

        <Route path="/leaderboard" element={<LeaderboardPage modalOpen={modalOpen} setModalOpen={setModalOpen}
        teamID={teamID} setTeamID={setTeamID}/>} />
        <Route path="/teams/:id" element={<TeamDetailPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
