window.SAMPLE_DATA = {
  questions: [
    {
      id: "sample-001",
      question:
        "What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?",
      answer: "Chief of Protocol of the United States",
      type: "bridge",
      level: "medium",
    },
    {
      id: "sample-002",
      question:
        "Are both The Golden Bowl and The Wings of the Dove novels by Henry James?",
      answer: "yes",
      type: "comparison",
      level: "easy",
    },
  ],
  graphs: {
    "sample-001": {
      question: {
        id: "sample-001",
        text:
          "What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?",
        type: "bridge",
        level: "medium",
      },
      answer: "Chief of Protocol of the United States",
      nodes: [
        {
          id: "q:sample-001",
          name:
            "What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?",
          category: "Question",
        },
        { id: "d:Kiss and Tell", name: "Kiss and Tell", category: "Document" },
        { id: "d:Shirley Temple", name: "Shirley Temple", category: "Document" },
        {
          id: "s:1",
          name: "The film stars Shirley Temple as Corliss Archer.",
          category: "Sentence",
        },
        {
          id: "s:2",
          name: "She served as Chief of Protocol of the United States.",
          category: "Sentence",
        },
        {
          id: "a:sample-001",
          name: "Chief of Protocol of the United States",
          category: "Answer",
        },
      ],
      links: [
        { source: "q:sample-001", target: "d:Kiss and Tell", name: "HAS_CONTEXT" },
        { source: "q:sample-001", target: "d:Shirley Temple", name: "HAS_CONTEXT" },
        { source: "d:Kiss and Tell", target: "s:1", name: "HAS_SENTENCE" },
        { source: "d:Shirley Temple", target: "s:2", name: "HAS_SENTENCE" },
        { source: "q:sample-001", target: "s:1", name: "SUPPORTS" },
        { source: "q:sample-001", target: "s:2", name: "SUPPORTS" },
        { source: "q:sample-001", target: "a:sample-001", name: "HAS_ANSWER" },
      ],
    },
    "sample-002": {
      question: {
        id: "sample-002",
        text:
          "Are both The Golden Bowl and The Wings of the Dove novels by Henry James?",
        type: "comparison",
        level: "easy",
      },
      answer: "yes",
      nodes: [
        {
          id: "q:sample-002",
          name:
            "Are both The Golden Bowl and The Wings of the Dove novels by Henry James?",
          category: "Question",
        },
        { id: "d:The Golden Bowl", name: "The Golden Bowl", category: "Document" },
        {
          id: "d:The Wings of the Dove",
          name: "The Wings of the Dove",
          category: "Document",
        },
        {
          id: "s:3",
          name: "The Golden Bowl is a 1904 novel by Henry James.",
          category: "Sentence",
        },
        {
          id: "s:4",
          name: "The Wings of the Dove is a 1902 novel by Henry James.",
          category: "Sentence",
        },
        { id: "a:sample-002", name: "yes", category: "Answer" },
      ],
      links: [
        { source: "q:sample-002", target: "d:The Golden Bowl", name: "HAS_CONTEXT" },
        {
          source: "q:sample-002",
          target: "d:The Wings of the Dove",
          name: "HAS_CONTEXT",
        },
        { source: "d:The Golden Bowl", target: "s:3", name: "HAS_SENTENCE" },
        { source: "d:The Wings of the Dove", target: "s:4", name: "HAS_SENTENCE" },
        { source: "q:sample-002", target: "s:3", name: "SUPPORTS" },
        { source: "q:sample-002", target: "s:4", name: "SUPPORTS" },
        { source: "q:sample-002", target: "a:sample-002", name: "HAS_ANSWER" },
      ],
    },
  },
  clusters: {
    type: [
      { name: "bridge", count: 1 },
      { name: "comparison", count: 1 },
    ],
    level: [
      { name: "medium", count: 1 },
      { name: "easy", count: 1 },
    ],
  },
};
