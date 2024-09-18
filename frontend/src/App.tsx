import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";
import CreateMatchResult from "./components/forms/CreateMatchResult";
import CreateTeam from "./components/forms/CreateTeam";
import Header from "./components/commons/Header";
import HomePage from "./pages/home/HomePage";
import TeamDetailPage from "./pages/team_detail_page/TeamDetailPage";

function App() {
  return (
    <Router>
      {/* Header banner */}
      <Header/>
      {/* Routes to pages */}
      <Routes>
        <Route path="/" element={<HomePage/>}/>
        <Route path="/teams/:id" element={<TeamDetailPage/>}/>
        <Route path="/create_team" element={<CreateTeam/>}/>
        <Route path="/create_match_result" element={<CreateMatchResult/>}>
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
