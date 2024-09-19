import React, { useEffect, useRef, useState } from "react";
import {
  BatchRegisterTeamRequest,
  RegisterTeamRequest,
  RegisterTeamRequestSchema,
} from "../../types/team";
import { z } from "zod";
import Button from "../commons/Button";
import { Result } from "../../types/generic";
import TeamService from "../../api/teamService";

const CreateTeamForm = () => {
  const [text, setText] = useState("");
  const [counter, setCounter] = useState<number>(0); // forces re-render
  const [showPopup, setShowPopup] = useState<boolean>(false);
  const [consoleText, setConsoleText] = useState<string>("");
  const consoleRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const highlightRef = useRef<HTMLDivElement>(null);

  const appendToConsole = (text: string) => {
    setConsoleText(consoleText + text + "\n---\n");
  };

  const getCursorLineNumber = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      const cursorPosition = textarea.selectionStart;
      const textBeforeCursor = textarea.value.substring(0, cursorPosition);
      const lineNumber = textBeforeCursor.split("\n").length;
      return lineNumber;
    }
    return 0;
  };

  const getResultIfLinePass = (line: string): Result<RegisterTeamRequest> => {
    const splitLine = line.trim().split(/\s+/);
    if (splitLine.length != 3) {
      return { error: new Error("not length 3") };
    }
    const [teamName, registrationDate, groupNumber] = [
      String(splitLine[0]),
      splitLine[1],
      Number(splitLine[2]),
    ];
    const registrationTeamRequest: RegisterTeamRequest = {
      team_name: teamName,
      registration_date_ddmm: registrationDate,
      group_number: groupNumber,
    };
    try {
      RegisterTeamRequestSchema.parse(registrationTeamRequest);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return { error: err };
      }
    }
    return { value: registrationTeamRequest };
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const payload: BatchRegisterTeamRequest = {
      teams: [],
    };

    const lines: string[] = text.split("\n");
    lines.forEach((line: string) => {
      // passed
      const result = getResultIfLinePass(line);
      if ("value" in result) {
        payload.teams.push(result.value);
      }
    });
    if (payload.teams.length === 0) {
      return;
    }

    try {
      const response = await TeamService.createTeams(payload);

      if (response.ok) {
        appendToConsole(
          "body:\n" + JSON.stringify(payload) + "\nServer Response:\nsuccess"
        );
        setText(""); // Reset the form
      } else {
        const jsonData = await response.json();
        appendToConsole(
          "body:\n" +
            JSON.stringify(payload) +
            "\nServer Response:\nerror:" +
            JSON.stringify(jsonData)
        );
      }
    } catch (error) {
      appendToConsole(
        "body:\n" +
          JSON.stringify(payload) +
          "\nServer Response:\nerror:\n " +
          error
      );
    }
  };

  // Function to highlight
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const getHighlightedText = (text: string, _counter: number) => {
    // split into lines
    const splitBy = "\n";
    const splitText = text.split(splitBy);
    return splitText.map((line, index) => {
      const errorArray: string[] = [];
      // queue checks
      const strippedLine = line.trim();
      // split by whitespace of variable length
      const splitLine = strippedLine.split(/\s+/);
      if (splitLine[0].length === 0) {
        splitLine.shift();
      }
      // check if the line has 3 elements
      if (splitLine.length > 3) {
        errorArray.push("❌ expected 3 args only");
      } else if (splitLine.length <= 3) {
        if (splitLine.length > 1) {
          const registrationDate = splitLine[1];
          try {
            RegisterTeamRequestSchema.shape.registration_date_ddmm.parse(
              registrationDate
            );
          } catch (err) {
            if (err instanceof z.ZodError) {
              errorArray.push(`❌ ${err.issues[0].message}`);
            }
          }
        }

        if (splitLine.length > 2) {
          const groupNumber = Number(splitLine[2]);
          try {
            RegisterTeamRequestSchema.shape.group_number.parse(groupNumber);
          } catch (err) {
            if (err instanceof z.ZodError) {
              errorArray.push(`❌ ${err.issues[0].message}`);
            }
          }
        }
        if (splitLine.length === 0) {
          errorArray.push("<team name>");
        }
        if (splitLine.length <= 1) {
          errorArray.push("<registration date>");
        }
        if (splitLine.length <= 2) {
          errorArray.push("<group number>");
        }
      }
      const cursorLineNumber = getCursorLineNumber();
      return errorArray.length === 0 ? (
        <>
          <span key={index} className="bg-green-400 rounded p-[3px]">
            {line}
          </span>
          {cursorLineNumber === index + 1 ? (
            <span className="absolute bg-white z-[100] text-black mx-2 p-1 outline outline-1 text-[10px] text-nowrap   rounded">
              ✅ correct format
            </span>
          ) : (
            <span className="absolute bg-white z-[1] text-black mx-2 p-1  text-[10px] text-nowrap   rounded">
              ✅
            </span>
          )}

          {splitBy}
        </>
      ) : (
        <>
          <span key={index} className="bg-red-400 rounded p-[3px]">
            {line}
          </span>
          {cursorLineNumber === index + 1 && showPopup ? (
            <span className=" absolute z-[100] bg-white fixed text-black mx-2 p-1 outline outline-1 text-[10px]  rounded">
              {errorArray.join("\n")}
            </span>
          ) : (
            <span className=" absolute bg-white fixed text-black mx-2 p-1  text-[10px]  rounded">
              ❌
            </span>
          )}

          {splitBy}
        </>
      );
    });
  };

  // Synchronize scroll of textarea and highlight div
  const handleScroll = () => {
    if (highlightRef.current && textareaRef.current) {
      highlightRef.current.scrollTop = textareaRef.current.scrollTop;
      highlightRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [consoleText]);

  return (
    <div className="h-screen-less-all-headers w-article-wide flex justify-center flex-col items-center">
      <form
        onSubmit={handleSubmit}
        className="bg-blue-100 flex justify-center flex-col w-full items-center p-4 rounded-lg"
      >
        <h1 className="text-2xl self-start text-text-pop">Console</h1>
        <div
          ref={consoleRef}
          className="bg-black text-green-300 p-2 h-[200px] w-full overflow-y-scroll whitespace-pre-wrap break-words scroll-smooth"
        >
          {consoleText}
        </div>
        <h1 className="text-2xl self-start text-text-pop">Create Team</h1>
        {/* format */}
        <body className="text-xs self-start text-text-norm">
          Format: {"<"}team_name{">"} {"<"}registration_date{">"} {"<"}
          group_number{">"}{" "}
        </body>
        <body className="text-xs self-start text-text-norm">
          Transaction is atomic
        </body>
        <div style={{ position: "relative", width: "100%", height: "200px" }}>
          {/* The overlay div with highlighted text */}
          <div
            ref={highlightRef}
            className="absolute w-full h-full p-[8px] bg-white color-transparent whitespace-pre-wrap break-words overflow-y-auto pointer-events-none resize-none"
          >
            <div style={{ color: "transparent", whiteSpace: "pre-wrap" }}>
              {text.length > 0 && getHighlightedText(text, counter)}
            </div>
          </div>

          {/* The textarea itself for editing */}
          <div className="border border-black w-full h-[200px] relative">
            <textarea
              ref={textareaRef}
              className="w-full h-full absolute top-0 left-0 p-[8px] bg-transparent text-black whitespace-pre-wrap break-words  resize-none"
              value={text}
              onClick={() => {
                setCounter((counter) => counter + 1);
                setShowPopup(true);
              }}
              onKeyUp={()=>{
                setCounter((counter) => counter + 1);
              }}
              onBlur={() => {
                setShowPopup(false);
              }}
              onChange={(e) => setText(e.target.value)}
              onScroll={handleScroll}
              placeholder="<team_name> <registration_date> <group_number>"
            />
          </div>
        </div>
        <Button
          onClick={() => {
            console.log("clicked");
          }}
        >
          Submit
        </Button>
      </form>
    </div>
  );
};

export default CreateTeamForm;
