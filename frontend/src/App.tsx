import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CreateMatchResultForm from "./components/forms/CreateMatchResultForm";
import CreateTeamForm from "./components/forms/CreateTeamForm";
import Header from "./components/commons/Header";
import HomePage from "./pages/home/HomePage";
import TeamDetailPage from "./pages/team_detail_page/TeamDetailPage";
import CreateTeamPage from "./pages/admin/CreateTeamPage";
import CreateMatchupPage from "./pages/admin/CreateMatchupPage";

function App() {
  return (
    <Router>
      {/* Header banner */}
      <Header />
      {/* Routes to pages */}
      <Routes>
        <Route path="/admin" element={<HomePage />}>
          <Route
            path="team"
            element={<CreateTeamPage />}
          />
          <Route
            path="matchup"
            element={<CreateMatchupPage />}
          />
        </Route>
        <Route path="/teams/:id" element={<TeamDetailPage />} />
        <Route path="/create_team" element={<CreateTeamForm />} />
      </Routes>
    </Router>
  );
}

export default App;
