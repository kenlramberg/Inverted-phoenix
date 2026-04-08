import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import '@/App.css';
import Landing from '@/pages/Landing';
import Ask from '@/pages/Ask';
import Evaluate from '@/pages/Evaluate';
import Contribute from '@/pages/Contribute';
import Search from '@/pages/Search';
import Coordinate from '@/pages/Coordinate';
import Execute from '@/pages/Execute';
import Journey from '@/pages/Journey';
import RequestDetail from '@/pages/RequestDetail';
import GivingPoll from '@/pages/GivingPoll';
import WhatCanYouGive from '@/pages/WhatCanYouGive';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/ask" element={<Ask />} />
        <Route path="/evaluate" element={<Evaluate />} />
        <Route path="/contribute" element={<Contribute />} />
        <Route path="/search" element={<Search />} />
        <Route path="/coordinate" element={<Coordinate />} />
        <Route path="/execute" element={<Execute />} />
        <Route path="/journey" element={<Journey />} />
        <Route path="/request/:id" element={<RequestDetail />} />
        <Route path="/poll" element={<GivingPoll />} />
        <Route path="/give" element={<WhatCanYouGive />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
