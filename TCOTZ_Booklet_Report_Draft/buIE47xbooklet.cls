%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%                         Bilkent University                             %% 
%%            IE 477 Production Systems Design - Synthesis                %%
%%            IE 478 Production Systems Design - Practice                 %%
%%                      Booklet LaTeX class file                          %%
%%                                                                        %%
%%                                                                        %%
%% Ver 1.0 on March 25, 2022                                              %% 
%%   Created by Prof. Dr. Savaş Dayanık                                   %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% --- Class structure: identification part

\ProvidesClass{buIE47xbooklet}[2022/03/25 version 1.0]
\NeedsTeXFormat{LaTeX2e}

% --- Class structure: initial code part

\RequirePackage{ifthen} 
\RequirePackage{calc}   % needed in rmarkdown template
\newboolean{@rmarkdown}
% @rmarkdown is set by R Markdown latex template to true. This
% will be useful to take actions necessary if we write LaTeX report but not
% if we write R Markdown report. For example, R Markdown (actually pandoc)
% automatically Bibliography to table of contents, but LaTeX does not. We
% used @rmarkdown in AtEndDocument below to add Bibliography to LaTeX ToC, but
% avoid a second ToC entry in R Markdown.

% --- Class structure: declaration of options part

\DeclareOption{letterpaper}{\OptionNotUsed}
\DeclareOption{legalpaper}{\OptionNotUsed}
\DeclareOption{executivepaper}{\OptionNotUsed}
\DeclareOption{landscape}{\OptionNotUsed}
\DeclareOption{a5paper}{\OptionNotUsed}
\DeclareOption{b5paper}{\OptionNotUsed}
\DeclareOption{10pt}{\OptionNotUsed}
\DeclareOption{11pt}{\OptionNotUsed}
\DeclareOption{twoside}{\OptionNotUsed}
\DeclareOption{twocolumn}{\OptionNotUsed}
\DeclareOption{titlepage}{\OptionNotUsed}

% cover page contains project short name and team number. 
\newboolean{@nocoverpage} % Every newly declared boolean is set to false by default.
\DeclareOption{nocoverpage}{\setboolean{@nocoverpage}{true}}

% print option disable colors and hyperlinks for printing
\newboolean{@print} % Every newly declared boolean is set to false by default.
\DeclareOption{print}{\setboolean{@print}{true}}

% --- Class structure: execution of options part

\ProcessOptions \relax

% --- Class structure: declaration of options part

\LoadClass[oneside,12pt]{article}

\RequirePackage[utf8]{inputenc}      % for Turkish characters
%\RequirePackage[english]{babel}
%https://tex.stackexchange.com/questions/32178/usepackageturkishbabel-and-includegraphics-inconcistency
\RequirePackage[turkish,english,shorthands=:!]{babel}
% https://tex.stackexchange.com/questions/313615/custom-paper-size-geometry-package-class
% \RequirePackage[top=3cm,bottom=3cm,left=3.5cm,right=3.5cm]{geometry}
\RequirePackage{geometry}
\geometry{
  paperheight=24cm,
  paperwidth=16.5cm,
  margin=1.5cm,
  headheight=1cm,
  headsep=0.2cm,
  footskip=.75cm  
  % layoutsize={4.25in,7in},
  % layoutoffset={.5in,.5in},
  % showcrop,
}

% Use in paper preamble \addtitlepagetop, \addtitlepagebottom, \addtitlepageleft, \addtitlepageright with negative lengths
% (e.g., \addtitlepagetop{-1cm}) to enlarge titlepage margins if necessary (e.g., to fit all material into one page)
\newlength{\@titlepagetop}
\setlength{\@titlepagetop}{1.5cm}
\newcommand{\addtitlepagetop}[1]{\addtolength{\@titlepagetop}{#1}}
\newlength{\@titlepagebottom}
\setlength{\@titlepagebottom}{1.5cm}
\newcommand{\addtitlepagebottom}[1]{\addtolength{\@titlepagebottom}{#1}}
\newlength{\@titlepageleft}
\setlength{\@titlepageleft}{1.5cm}
\newcommand{\addtitlepageleft}[1]{\addtolength{\@titlepageleft}{#1}}
\newlength{\@titlepageright}
\setlength{\@titlepageright}{1.5cm}
\newcommand{\addtitlepageright}[1]{\addtolength{\@titlepageright}{#1}}

\RequirePackage{amsmath, amssymb}    % for math
%\RequirePackage{newtxtext}           % for Times New Roman font
% https://tex.stackexchange.com/questions/182874/control-line-spacing-of-section-headings
% https://tex.stackexchange.com/questions/29911/titlesec-vertical-space-that-i-dont-want (added \lineskiplimit=-\maxdimen
\RequirePackage{setspace}
% titlesec compact option reduces space left before and after section, subsection, subsubsection titles
% titleformat commands reduce the spaces between lines in the section, subsection, subsubsection titles
\RequirePackage[compact]{titlesec}
\titleformat{\section}{\normalfont\Large\bfseries\lineskiplimit=-\maxdimen}{\thesection}{1em}{\setstretch{1}}
\titleformat{\subsection}{\normalfont\large\bfseries\lineskiplimit=-\maxdimen}{\thesubsection}{1em}{\setstretch{1}}
\titleformat{\subsubsection}{\normalfont\bfseries\lineskiplimit=-\maxdimen}{\thesubsubsection}{1em}{\setstretch{1}}
\RequirePackage{anyfontsize}         % for the number on the title
\RequirePackage{makeidx}             % for generating index
\RequirePackage{array}               % extend options of tabular  
\RequirePackage{longtable}           % for long tables
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
% 2 May 2024
% If a longtable and floating environment are on the same page, then longtable miscalculates the page length
% and text overflow occurs. Below we apply a fix due to package author. This piece has to be sitting after longtable and
% before hyperref
% Longtable problem fix starts
% https://tex.stackexchange.com/questions/558439/page-overflows-when-using-longtable-and-floats-on-same-page
% SD: commented out \makeatletter lines because the original fix is supposed to be used in a latex document
% \makeatletter
\def\LT@start{%
  \let\LT@start\endgraf
  \endgraf\penalty\z@\vskip\LTpre\endgraf
  \dimen@\pagetotal
  \advance\dimen@ \ht\ifvoid\LT@firsthead\LT@head\else\LT@firsthead\fi
  \advance\dimen@ \dp\ifvoid\LT@firsthead\LT@head\else\LT@firsthead\fi
  \advance\dimen@ \ht\LT@foot
  \dimen@ii\vfuzz
  \vfuzz\maxdimen
  \setbox\tw@\copy\z@
  \setbox\tw@\vsplit\tw@ to \ht\@arstrutbox
  \setbox\tw@\vbox{\unvbox\tw@}%
  \vfuzz\dimen@ii
  \advance\dimen@ \ht
  \ifdim\ht\@arstrutbox>\ht\tw@\@arstrutbox\else\tw@\fi
  \advance\dimen@\dp
  \ifdim\dp\@arstrutbox>\dp\tw@\@arstrutbox\else\tw@\fi
  \advance\dimen@ -\pagegoal
  \ifdim \dimen@>\z@\vfil\break\fi
  \global\@colroom\@colht
  \ifvoid\LT@foot\else
  % \advance\vsize-\ht\LT@foot
  \global\advance\vsize-\ht\LT@foot
  \global\advance\@colroom-\ht\LT@foot
  \dimen@\pagegoal\advance\dimen@-\ht\LT@foot\pagegoal\dimen@
  \maxdepth\z@
  \fi
  \ifvoid\LT@firsthead\copy\LT@head\else\box\LT@firsthead\fi\nobreak
  \output{\LT@output}}

\def\endlongtable{%
  \crcr
  \noalign{%
    \let\LT@entry\LT@entry@chop
    \xdef\LT@save@row{\LT@save@row}}%
  \LT@echunk
  \LT@start
  \unvbox\z@
  \LT@get@widths
  \if@filesw
  {\let\LT@entry\LT@entry@write\immediate\write\@auxout{%
      \gdef\expandafter\noexpand
      \csname LT@\romannumeral\c@LT@tables\endcsname
      {\LT@save@row}}}%
  \fi
  \ifx\LT@save@row\LT@@save@row
  \else
  \LT@warn{Column \@width s have changed\MessageBreak
    in table \thetable}%
  \LT@final@warn
  \fi
  \endgraf\penalty -\LT@end@pen
  % 
  \ifvoid\LT@foot\else
  \global\advance\vsize\ht\LT@foot
  \global\advance\@colroom\ht\LT@foot
  \dimen@\pagegoal\advance\dimen@\ht\LT@foot\pagegoal\dimen@
  \fi
  % 
  \endgroup
  \global\@mparbottom\z@
  % \pagegoal\vsize
  \endgraf\penalty\z@\addvspace\LTpost
  \ifvoid\footins\else\insert\footins{}\fi}

\def\LT@output{%
  \ifnum\outputpenalty <-\@Mi
  \ifnum\outputpenalty > -\LT@end@pen
  \LT@err{floats and marginpars not allowed in a longtable}\@ehc
  \else
  \setbox\z@\vbox{\unvbox\@cclv}%
  \ifdim \ht\LT@lastfoot>\ht\LT@foot
  \dimen@\pagegoal
  % 
  \advance\dimen@\ht\LT@foot
  % 
  \advance\dimen@-\ht\LT@lastfoot
  \ifdim\dimen@<\ht\z@
  \setbox\@cclv\vbox{\unvbox\z@\copy\LT@foot\vss}%
  \@makecol
  \@outputpage
  % 
  \global\vsize\@colroom
  % 
  \setbox\z@\vbox{\box\LT@head}%
  \fi
  \fi
  % \global\@colroom\@colht
  % \global\vsize\@colht
  % \vbox
  % {\unvbox\z@\box\ifvoid\LT@lastfoot\LT@foot\else\LT@lastfoot\fi}%
  \unvbox\z@\ifvoid\LT@lastfoot\copy\LT@foot\else\box\LT@lastfoot\fi
  \fi
  \else
  \setbox\@cclv\vbox{\unvbox\@cclv\copy\LT@foot\vss}%
  \@makecol
  \@outputpage
  \global\vsize\@colroom
  \copy\LT@head\nobreak
  \fi}

% \makeatother
% Longtable problem fix end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
\RequirePackage{booktabs}            % for tables
\RequirePackage{graphicx}            % for including graphics
\RequirePackage{natbib}              % for citation
\RequirePackage{listings}			 % for code lists
\RequirePackage{lscape}
\RequirePackage[hyphens]{url}
\RequirePackage{fancyhdr}
% https://github.com/schnorr/infufrgs/issues/28
% 20240413: Added xcolor package to avoid compilation error for the diff tex file produced
% by latexdiff command (track changes). Otherwise the package was loaded bby hyperref
% automatically, I guess. -- SD 
\RequirePackage{xcolor}
\renewcommand{\headrulewidth}{0pt}
\fancyhead[L,C,R]{}
\pagestyle{fancy}

% https://tex.stackexchange.com/questions/71129/bibliography-in-table-of-contents
\ifthenelse{\boolean{@rmarkdown}}{}{\RequirePackage[nottoc,notlot,notlof]{tocbibind}}

\renewcommand{\refname}{Bibliography}

%%%%%%%%% hyperref package should be loaded after all other packages are loaded %%%%%%%%%%%%%%%%%%%%%%%
% https://tex.stackexchange.com/questions/50747/options-for-appearance-of-links-in-hyperref
% \RequirePackage[colorlinks=false]{hyperref}
% \hypersetup{hidelinks=true}
\ifthenelse{\boolean{@print}}{
%   \RequirePackage[colorlinks=false,breaklinks,hidelinks]{hyperref}
	\RequirePackage[draft]{hyperref}
}{
	\RequirePackage[colorlinks=true,bookmarksnumbered,breaklinks]{hyperref} % for hyperlinks
	\hypersetup{  
		urlcolor=blue,
		citecolor=blue,
		linkcolor=blue}
}
% https://stackoverflow.com/questions/4023925/how-to-make-a-hyperlink-navigate-to-the-top-of-the-figure-in-latex-when-using-hy  
% Make sure caption placed AFTER hyperref. It sets hypcap=TRUE and anchors hyperlinks to the beginning of an environment.
\usepackage{caption}

% Table captions are above the tables. Below we set the space between caption and table to the height of one line.
% \renewcommand{\belowcaptionskip}{\baselineskip}
% The following did not work with listings package. Listings cannot handle
% numbers in the new value. Therefore we are gong to define new length variable
% \renewcommand{\belowcaptionskip}{-0.75\baselineskip}
\newlength{\mybelowcaptionskip}
\setlength{\mybelowcaptionskip}{-0.75\baselineskip}
\renewcommand{\belowcaptionskip}{\mybelowcaptionskip}

% --- Class structure: main code part

% Generic project info command
% \newcommand{\@...}{Use ``\textbackslash ...'' (LaTeX) of ``...'' (R Markdown) to enter ....} % default
% \newcommand{\...}[1]{\renewcommand{\@...}{\textbf{#1}}}      % user can change its value

% Company name
\newcommand{\@TRcompany}{|Use ``\textbackslash TRcompany'' (LaTeX) or ``TRcompany:'' (R Markdown) to enter TRcompany name|}
\newcommand{\TRcompany}[1]{\renewcommand{\@TRcompany}{#1}}

% Project name
\newcommand{\@TRprojectname}{|Use ``\textbackslash project'' (LaTeX) or ``project\_name:'' (R Markdown) to enter project name|} 
\newcommand{\@TRprojectnameToC}{|Use ``\textbackslash project'' (LaTeX) or ``project\_name:'' (R Markdown) to enter project name|} 
% use optional argument to give an alternative title for table of contents
\newcommand{\TRprojectname}[2][]{  
  \renewcommand{\@TRprojectname}{#2}
  \ifthenelse{\equal{#1}{}}{\renewcommand{\@TRprojectnameToC}{#2}}{\renewcommand{\@TRprojectnameToC}{#1}}
}


\newcommand{\@ENGprojectname}{|Use ``\textbackslash project'' (LaTeX) or ``project\_name:'' (R Markdown) to enter project name|} 
\newcommand{\@ENGprojectnameToC}{|Use ``\textbackslash project'' (LaTeX) or ``project\_name:'' (R Markdown) to enter project name|}
% use optional argument to give an alternative title for table of contents
\newcommand{\ENGprojectname}[2][]{
  \renewcommand{\@ENGprojectname}{#2}
  \ifthenelse{\equal{#1}{}}{\renewcommand{\@ENGprojectnameToC}{#2}}{\renewcommand{\@ENGprojectnameToC}{#1}}  
}

% Project short code
\newcommand{\@projectshortcode}{|Use ``\textbackslash projectshortcode'' (LaTeX) or ``project\_short\_code:'' (R Markdown) to enter project short code|}
\newcommand{\projectshortcode}[1]{\renewcommand{\@projectshortcode}{#1}}

% Team number 
\newcommand{\@teamno}{|Use ``\textbackslash teamno'' (LaTeX) or ``team\_no:'' (R Markdown) to enter team no|}
\newcommand{\teamno}[1]{\renewcommand{\@teamno}{#1}}

% Team members
\newcommand{\@teammembers}{|Use ``\textbackslash teammembers'' (LaTeX) or ``team\_members:'' (R Markdown)  to enter team members|}
\newcommand{\teammembers}[1]{\renewcommand{\@teammembers}{#1}}

% Industrial advisor(s)
\newcommand{\@IA}{|Use ``\textbackslash IA'' (LaTeX) or ``industrial\_advisors:'' (R Markdown) to enter full name and department of industrial advisor(s)|}
%\newcommand{\IA}[1]{\renewcommand{\@IA}{#1}}
\newboolean{@IAteam} % Is IA a team? By default it is false.
\newcommand{\IA}[2][]{
	\renewcommand{\@IA}{#2}
	\ifthenelse{\equal{#1}{team}}{\setboolean{@IAteam}{true}}{\relax}
}

% Academic advisor(s)
\newcommand{\@AA}{|Use ``\textbackslash AA'' (LaTeX) or ``academic\_advisors:'' (R Markdown) to enter full name and department of academic advisor(s)|}
%\renewcommand{\AA}[1]{\renewcommand{\@AA}{#1}}
\newboolean{@AAteam} % Is AA a team? By default it is false.
\renewcommand{\AA}[2][]{
	\renewcommand{\@AA}{#2}
	\ifthenelse{\equal{#1}{team}}{\setboolean{@AAteam}{true}}{\relax}
}


% TRabstract
\newcommand{\@TRabstract}{|Use ``\textbackslash TRabstract'' (LaTeX) or ``TRabstract:'' (R Markdown) to enter an TRabstract for the project.|}
\newcommand{\TRabstract}[1]{\renewcommand{\@TRabstract}{#1}}

% ENGabstract
\newcommand{\@ENGabstract}{|Use ``\textbackslash ENGabstract'' (LaTeX) or ``ENGabstract:'' (R Markdown) to enter an ENGabstract for the project.|}
\newcommand{\ENGabstract}[1]{\renewcommand{\@ENGabstract}{#1}}

% TRkeywords
\newcommand{\@TRkeywords}{|Use ``\textbackslash TRkeywords'' (LaTeX) or ``TRkeywords:'' (R Markdown) to enter TRkeywords that describe your project|}
\newcommand{\TRkeywords}[1]{\renewcommand{\@TRkeywords}{#1}}

% ENGkeywords
\newcommand{\@ENGkeywords}{|Use ``\textbackslash ENGkeywords'' (LaTeX) or ``ENGkeywords:'' (R Markdown) to enter ENGkeywords that describe your project|}
\newcommand{\ENGkeywords}[1]{\renewcommand{\@ENGkeywords}{#1}}

% Acknowledgment optional
\newboolean{@ackexists} % Every newly declared boolean is set to false by default.
\newcommand{\@ack}{}
\newcommand{\ack}[1]{%
  \setboolean{@ackexists}{true}
  \renewcommand{\@ack}{#1}
}

% Use \date{} command if you want to print a date different than today.
% \date{13 Sep 2021}

% Reformat date
\renewcommand{\today}{\number \day\ \ifcase \month \or January\or February\or March\or %
April\or May \or June\or July\or August\or September\or October\or November\or %
December\fi\ \number \year} 

% Bibtex file name
\newcommand{\@bibfilename}{\relax}                              % no default bibfile name
\newcommand{\bibfilename}[1]{\renewcommand{\@bibfilename}{#1}}  % user can change

% Team photo file name
\newcommand{\@teamphoto}{}                                      % no default photo file name
\newcommand{\teamphoto}[1]{\renewcommand{\@teamphoto}{#1}}      % user can change

% Inspired by the redefined \secformat on p. 41 of The LaTeX Companion,
% Mittelbach and Goossens, 2nd Edition and
% https://tex.stackexchange.com/questions/265/fonts-larger-than-huge
% \newcommand\fancytitle{%
% 	\begin{minipage}[c]{0.80\linewidth}
% 		\filleft\bfseries\Large \@TRprojectname%	
% 	\end{minipage}%
% 	\quad%
% 	\begin{minipage}[c]{2pt}
% 		\rule[-12pt]{2pt}{60pt}
% 	\end{minipage}%
% 	\quad%
% 	\begin{minipage}[c]{0.10\linewidth}
% %	\resizebox{\linewidth}{!}{\@teamno}
% 	\fontsize{45}{10}\selectfont\@teamno
% 	\end{minipage}
% }

\newsavebox{\projnamebox}
\newsavebox{\rulebox}
\newsavebox{\numbox}
% Inspired by the redefined \secformat on p. 41 of The LaTeX Companion,
% Mittelbach and Goossens, 2nd Edition and
% https://tex.stackexchange.com/questions/265/fonts-larger-than-huge
\newcommand\fancytitle[1][right]{%
  % optional left/right argument puts the team number to the left/right of
  % project title.
  \sbox{\projnamebox}{%
    \begin{minipage}[c]{0.80\linewidth}
      \ifthenelse{\equal{#1}{right}}{\filleft}{\filright}\bfseries\Large \@TRprojectname%
    \end{minipage}%
  }

  \sbox{\rulebox}{%
    \begin{minipage}[c]{2pt}
      \rule[-12pt]{2pt}{60pt}
    \end{minipage}%
  }

  \sbox{\numbox}{
    \begin{minipage}[c]{0.10\linewidth}
      % \resizebox{\linewidth}{!}{\@teamno}
      % \fontsize{45}{10}\selectfont\@teamno
      \fontsize{45}{10}\selectfont\@teamno
    \end{minipage}%
  }

  \ifthenelse{\equal{#1}{right}}{
    \usebox{\projnamebox}%
    \quad%
    \usebox{\rulebox}%
    \quad%
    \usebox{\numbox}%
  }{
    \usebox{\numbox}%
    \quad%
    \usebox{\rulebox}%
    \quad%
    \usebox{\projnamebox}%    
  }  
}


%\titleformat{\section}[block]
%{\filleft\normalfont\sffamily}{}{0pt}{\secformat}
%\titlespacing*{\section}{0pt}{*3}{*2}[1pc]

% title page
\renewcommand{\maketitle}{

  % print project short name and team number only on the converpage
  % if nocoverpage option is removed.
  \ifthenelse{\boolean{@nocoverpage}}{
	%https://tex.stackexchange.com/questions/115932/on-the-basics-of-writing-to-reading-from-auxiliary-files-aux-toc-etc
	\write\@auxout{\gdef\string\IE47xmessage{coverpagenotadded}}  
	}{
    \thispagestyle{empty}
    \vspace*{\fill}    
    {\centering \Huge \@projectshortcode \par Team \@teamno \par}
    \vspace*{\fill}  
    %    https://tex.stackexchange.com/questions/115932/on-the-basics-of-writing-to-reading-from-auxiliary-files-aux-toc-etc
    \write\@auxout{\gdef\string\IE47xmessage{coverpageadded}}
    \clearpage
  }
  
  \setcounter{page}{1}
%  \thispagestyle{empty}  
  {\centering
    \phantomsection % needed to make sure hyperref add proper link to Title page section in ToC correctly
	\addcontentsline{toc}{section}{Title and Abstract}

    % print project name
%    {\linespread{1.1}\selectfont \Large \bfseries \@TRprojectname \par}
    \fancytitle
    \vspace{0.5\baselineskip}

    % print TRcompany name
    {\linespread{1.1}\selectfont \Large \bfseries \@TRcompany \par}
    \vspace{0.5\baselineskip}

    \vfill

     % team photo
    \IfFileExists{\@teamphoto}{%
      \includegraphics[width=0.6\linewidth,draft=false]{\@teamphoto}%
    }{%
      \vfill
      \fbox{
        \parbox{0.5\textwidth}{Photo file is not found. Check if the photo filename is correct.}
       }
      \vfill
    }
    \vspace{0.5\baselineskip}


    
    % print team members
    \begin{minipage}{1.0\linewidth} \normalfont \centering
      \textbf{Proje Ekibi} \par
      \linespread{1}\selectfont \@teammembers
    \end{minipage}
    \vspace{0.5\baselineskip}
   
    
    % \large \linespread{1.1}\selectfont

    % print the address of team members
    % Industrial Engineering \par
    % Bilkent University \par
    % 06800 Ankara\par
    % \vspace{0.5\baselineskip}

    % % print industrial advisor full names and their departments
    % \textbf{Industrial Advisor(s)}\par \@IA\par \vspace{0.5\baselineskip}

    % % print academic advisor full names and their departments
    % \textbf{Academic Advisor(s)}\par \@AA\par \vspace{0.5\baselineskip}

    \begin{minipage}[t]{0.5\linewidth}
      \centering
      %      \textbf{Şirket Danışmanı}\par \@IA\par
      \ifthenelse{\boolean{@IAteam}}{\textbf{Şirket Danışmanları}}{\textbf{Şirket Danışmanı}}\par \@IA\par
    \end{minipage}%
    \begin{minipage}[t]{0.5\linewidth}
      \centering
%      \textbf{Akademik Danışman}\par \@AA\par
      \ifthenelse{\boolean{@AAteam}}{\textbf{Akademik Danışmanlar}}{\textbf{Akademik Danışman}}\par \@AA\par
    \end{minipage}
    \vspace{0.5\baselineskip}

    % % print date
    % \@date\par
    %     \vspace{.8\baselineskip}
    
    \vfill

    \begin{minipage}{1.0\linewidth}
      \begin{otherlanguage}{turkish}
  	\normalsize \linespread{1}\selectfont
	% print TRabstract
	% {\centering \normalfont \bfseries \abstractname \par}
        {\centering \normalfont \bfseries ÖZET \par}
	\noindent\@TRabstract\par\vspace{0.2\baselineskip}
	\noindent\textbf{Anahtar Sözcükler:} \@TRkeywords
      \end{otherlanguage}
  \end{minipage}
  } % centering
  \clearpage  
  }
  
%\linespread{1.2}
  \AtBeginDocument{
    % Produce title page with or without coverpage

	% Use in paper preamble \addtitlepagetop, \addtitlepagebottom, \addtitlepageleft, \addtitlepageright with negative lengths
	% (e.g., \addtitlepagetop{-1cm}) to enlarge titlepage margins if necessary (e.g., to fit all material into one page)
	% https://stackoverflow.com/questions/1670463/latex-change-margins-of-only-a-few-pages/44439837#44439837
    \newgeometry{top=\the\@titlepagetop, bottom=\the\@titlepagebottom, left=\the\@titlepageleft, right=\the\@titlepageright}    
    \maketitle
    \restoregeometry     %so it does not affect the rest of the pages.
    % produce table of contents
    % \tableofcontents

  {\centering \Large \bfseries \@ENGprojectname \par}
  \vspace{0.5\baselineskip}
  
  {\centering \normalfont \bfseries \abstractname \par}
  \noindent\@ENGabstract\par\vspace{0.2\baselineskip}
  \noindent\textbf{Keywords:} \@ENGkeywords

  }

\newboolean{@appendixexists} % Every newly declared boolean is set to false by default.
\let\origappendix\appendix % Keep original definition of \appendix to use later.
% If there is only one appendix, then use the optional argument to give a title, and
% Appendix: <Title> will print
     \renewcommand{\appendix}[1][]{
	% add acknowledgment and bibliography before the appendix
        \setboolean{@appendixexists}{true}
        % insert unnumbered acknowledgment section and add it to table of contents
        \ifthenelse{\boolean{@ackexists}}{%
          \phantomsection
          \section*{Acknowledgment}
          \addcontentsline{toc}{section}{Acknowledgment}
          
          \@ack
        }{\relax}%
	\bibliography{\@bibfilename}
	\bibliographystyle{chicago}
	
    % start appendices on a new page
    \clearpage
    %	https://tex.stackexchange.com/questions/44088/when-do-i-need-to-invoke-phantomsection	  
    \phantomsection % needed to make sure hyperref add proper link to Appendices section in ToC correctly
    % https://tex.stackexchange.com/questions/179964/how-to-test-if-a-string-is-empty
    \ifthenelse{\equal{#1}{}}{%
      \addcontentsline{toc}{section}{Appendices}
    }{%
      \addcontentsline{toc}{section}{Appendix}
    }
    % Before using original \appendix, we added entry to ToC for Appendices. If you add the entry after Appendices,
    % hyperlinks takes us below Appendices title of section.
    \origappendix
    \ifthenelse{\equal{#1}{}}{%
      \section*{Appendices}
    }{%
      \section*{Appendix: #1}
    }
    

%    %	https://tex.stackexchange.com/questions/444054/how-to-end-appendix
%    \setcounter{section}{0}%
%    \gdef\thesection{\@Alph\c@section}
}

  \AtEndDocument{
%      \clearpage      
    \ifthenelse{\boolean{@appendixexists}}{\relax}{
       \ifthenelse{\boolean{@ackexists}}{%
          \phantomsection
          \section*{Acknowledgment}
          \addcontentsline{toc}{section}{Acknowledgment}
          
          \@ack
        }{\relax}
  	\bibliography{\@bibfilename}
    \bibliographystyle{chicago}  
  }
  \clearpage
  \printindex
}
\allowdisplaybreaks
\makeindex
