import Foundation

// MARK: ErroRs

/// This is a customized error enum. It has type of (.allGood), (.notFound), (.httpError)
enum ERRoR: Error {
    case allGood
    case notFound(String)
    case httpError(Int, String)
}

// MARK: runCommand

/// This function will return the command's output,  the  state code and throw  an  ERRoR state
func runCommand(_ bin: String, isPrint: Bool = false, arguments: [String], runtime: Int = 1) throws -> (String, Int) {
    let pipe = Pipe()
    let file = pipe.fileHandleForReading
    var launchPath = bin

    if launchPath.first != "/" || launchPath != "/usr/bin/which" {
        launchPath = try! runCommand("/usr/bin/which", arguments: [launchPath], runtime: 2).0
    }

    if launchPath.isEmpty || launchPath.first != "/" {
        throw ERRoR.notFound("command not found")
    } else {
        if launchPath.last == "\n" {
            launchPath = String(launchPath.dropLast())
        }
        let task = Process()
        task.launchPath = launchPath
        task.arguments = arguments
        task.standardOutput = pipe
        try! task.run()
        task.waitUntilExit()

        let data = file.readDataToEndOfFile()
        if runtime == 1, isPrint {
            print(String(data: data, encoding: String.Encoding.utf8)!)
        }
        var returnString = String(data: data, encoding: String.Encoding.utf8)!
        if returnString.last == "\n" {
            returnString = String(returnString.dropLast())
        }
        return (returnString, Int(task.terminationStatus))
    }
}

import Foundation
// Basic Settings
let FManager = FileManager.default
// 输入目录
let inRootPath = "path/to/your/content/"
let inRootURL = URL(fileURLWithPath: rootPath)
let names = try! FManager.contentsOfDirectory(atPath: inRootURL.path)
// 输出目录
var outRootPath = "path/to/your/output/"
if !FManager.fileExists(atPath: outRootPath) {
    _ = try! runCommand("mkdir", arguments: ["\(outRootPath)"])
}

for pageName in names {
    let inputPath = inRootPath + "\(pageName).png"
    let outPath = outRootPath + "\(pageName).png"
    // 开始处理
    print("########################################")
    // 不要重复处理
    if FManager.fileExists(atPath: outPath) {
        print("##########FILE ALREADY EXISTED##########")
        print(outPath)
    } else {
        print(inputPath)
        // 这里调用了一个用于提高画质的开源软件(github.com/safx/waifu2x-metal)
        let exe = try! runCommand("path/to/your/waifu2x", arguments: ["--type", "a", "--scale", "2", "--noise", "4", "--input", inputPath, "--output", outPath])
        print(exe)
    }
}

print("@@@@@@OVER@@@@@@")
