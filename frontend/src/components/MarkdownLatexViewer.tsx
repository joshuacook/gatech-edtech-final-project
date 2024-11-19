import React from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface LaTeXViewerProps {
  content: string;
}

const LaTeXViewer = ({ content = '' }: LaTeXViewerProps) => {
  const processLatexBlock = (text: string) => {
    if (!text) return '';
    try {
      return katex.renderToString(text, {
        displayMode: true,
        throwOnError: false,
        trust: true,
        strict: false,
        macros: {
          "\\n": "\\\\",
        }
      });
    } catch (error) {
      console.error('KaTeX error:', error);
      return `<span class="text-red-500">Error rendering LaTeX: ${text}</span>`;
    }
  };

  const renderContent = () => {
    if (!content) return null;

    const displayMathPattern = /\$\$([\s\S]*?)\$\$/g;
    const inlineMathPattern = /\$([^\$]+)\$/g;
    
    let lastIndex = 0;
    const segments = [];
    let match;

    while ((match = displayMathPattern.exec(content)) !== null) {
      if (match.index > lastIndex) {
        segments.push({
          type: 'text',
          content: content.slice(lastIndex, match.index),
          index: lastIndex
        });
      }
      
      segments.push({
        type: 'display-math',
        content: match[1],
        index: match.index
      });
      
      lastIndex = match.index + match[0].length;
    }
    
    if (lastIndex < content.length) {
      segments.push({
        type: 'text',
        content: content.slice(lastIndex),
        index: lastIndex
      });
    }

    return segments.map((segment, index) => {
      if (segment.type === 'display-math') {
        return (
          <div key={index} className="my-4" dangerouslySetInnerHTML={{
            __html: processLatexBlock(segment.content)
          }} />
        );
      } else {
        const parts = [];
        let lastInlineIndex = 0;
        let inlineMatch;
        const textContent = segment.content;

        inlineMathPattern.lastIndex = 0;

        while ((inlineMatch = inlineMathPattern.exec(textContent)) !== null) {
          if (inlineMatch.index > lastInlineIndex) {
            const textPart = textContent.slice(lastInlineIndex, inlineMatch.index);
            parts.push(
              <span key={`text-${lastInlineIndex}`}>
                {textPart.split('\n').map((line, i, arr) => (
                  <React.Fragment key={i}>
                    {line}
                    {i < arr.length - 1 && <br />}
                  </React.Fragment>
                ))}
              </span>
            );
          }

          parts.push(
            <span key={`math-${inlineMatch.index}`} dangerouslySetInnerHTML={{
              __html: katex.renderToString(inlineMatch[1], {
                displayMode: false,
                throwOnError: false
              })
            }} />
          );

          lastInlineIndex = inlineMatch.index + inlineMatch[0].length;
        }

        if (lastInlineIndex < textContent.length) {
          const remainingText = textContent.slice(lastInlineIndex);
          parts.push(
            <span key={`text-${lastInlineIndex}`}>
              {remainingText.split('\n').map((line, i, arr) => (
                <React.Fragment key={i}>
                  {line}
                  {i < arr.length - 1 && <br />}
                </React.Fragment>
              ))}
            </span>
          );
        }

        return (
          <div key={index} className="min-h-[1.5em]">
            {parts}
          </div>
        );
      }
    });
  };

  return (
    <div className="prose prose-sm max-w-none space-y-1">
      {renderContent()}
    </div>
  );
};

export default LaTeXViewer;